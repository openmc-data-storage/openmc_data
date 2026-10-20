#!/usr/bin/env python3
"""Generate OpenMC HDF5 data from JEFF 3.3 or 4.0 ENDF evaluations using NJOY.

Requires njoy on PATH. Example:
    generate_jeff -r 4.0 -p neutron --temperatures 293.6 600 --jobs 4

Thermal scattering uses native temperatures, not --temperatures. Thermal-only
runs fetch neutron inputs without generating neutron HDF5. Photon supplements
use ENDF/B-VIII.0 for JEFF 3.3 and VIII.1 for 4.0.

NEA sources and published MD5s are in openmc_data.urls_jeff. Supported thermal
pairs are the 20 legacy 3.3 pairs and 128 upstream 4.0 pairs from:
https://github.com/openmc-dev/data/blob/master/generate_jeff.py
Additional temperature-split PuO2/UO2/Zy4 evaluations are excluded.
Full-library NJOY qualification has not been performed.

JEFF 3.3 C13/O17 use individual IAEA TENDL-2019 replacements without editing
originals. ZIP CRCs and ENDF targets are checked (no published MD5). If IAEA
blocks automated access, manually cache the archives; blocked downloads fail.

Output uses particle subdirectories and relative XML paths. Isolated workers
stage and validate outputs before publication; only current outputs are
registered. Processing failures preserve existing data. Publication removes
the old manifest first and installs the new one last.

Destination, download and ENDF directories must not overlap. Cache particle
subdirectories hold original archive basenames and nested inputs; 3.3
replacements use replacements/6-C-13g and replacements/8-O-17g beneath each
cache root. --no-download extracts cached archives, checking published MD5s.
With --no-download --no-extract, local neutron/photon subsets are allowed;
thermal runs require every mapped pair. --cleanup removes selected caches
only after success and only for enabled stages. --use-tmpdir is ignored with
a warning for reused inputs or explicit cache roots.
"""

import argparse
from contextlib import ExitStack
import math
from multiprocessing import Pool
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import warnings

from openmc_data import download, extract, process_neutron, process_thermal, ProgressTracker
from openmc_data.urls_jeff import jeff_endf_details, jeff33_replacements
from openmc_data.utils import _file_md5


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass


def _parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=CustomFormatter)
    parser.add_argument('-r', '--release', choices=['3.3', '4.0'], default='4.0',
                        help='JEFF release')
    parser.add_argument('-d', '--destination', type=Path, help='Output directory (default: jeff-RELEASE-hdf5)')
    parser.add_argument('-p', '--particles', nargs='+', choices=['neutron', 'thermal', 'photon'],
                        default=['neutron', 'thermal', 'photon'], help='Data types to generate')
    parser.add_argument('--temperatures', nargs='+', type=float,
                        default=[250.0, 293.6, 600.0, 900.0, 1200.0, 2500.0],
                        help='Neutron temperatures in kelvin (thermal uses native temperatures)')
    parser.add_argument('--jobs', type=int, default=None, help='NJOY worker count; default: CPU count')
    parser.add_argument('--libver', choices=['earliest', 'latest'], default='earliest',
                        help='Output HDF5 version compatibility')
    parser.add_argument('--download-dir', type=Path, help='Archive cache (default: jeff-RELEASE-download)')
    parser.add_argument('--endf-dir', type=Path, help='Extracted inputs (default: jeff-RELEASE-endf)')
    for flag, default, help_text in [
        ('download', True, 'Download missing or invalid archives'),
        ('extract', True, 'Extract archives into particle subdirectories'),
        ('cleanup', False, 'Remove selected caches after success, only for enabled download/extract stages'),
        ('use-tmpdir', False, 'Use temporary inputs for a fresh download and extraction'),
    ]:
        parser.add_argument('--' + flag, action='store_true', default=default, help=help_text)
        parser.add_argument('--no-' + flag, dest=flag.replace('-', '_'), action='store_false')
    return parser


def _prepare(details, archives, inputs, args):
    """Keep caches reusable offline and check checksums even with --no-download."""
    for name, checksum in zip(details['compressed_files'], details['checksums']):
        archive = archives / Path(name).name
        if args.download and not (archive.is_file() and checksum
                                  and _file_md5(archive) == checksum):
            download(details['base_url'] + name + details.get('url_suffix', ''),
                     checksum=checksum, output_path=archives,
                     output_filename=archive.name, timeout=60)
        if args.extract:
            if not archive.is_file():
                raise FileNotFoundError(f'Missing archive {archive}; enable --download or supply the cache')
            if checksum and _file_md5(archive) != checksum:
                raise OSError(f'MD5 checksum does not match: {archive}')
    if args.extract:
        # A fresh extraction avoids discovering stale evaluations left by an old archive.
        inputs.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix='.jeff-extract-', dir=inputs.parent) as tmp:
            staging = Path(tmp) / 'inputs'
            for name in details['compressed_files']:
                extract(archives / Path(name).name, staging)
            if inputs.exists():
                shutil.rmtree(inputs)
            staging.replace(inputs)


def _index(directory, pattern):
    result = {}
    for path in sorted(directory.rglob(pattern)):
        if path.is_file():
            if path.name in result:
                raise ValueError(f'Ambiguous input {path.name}: {result[path.name]} and {path}')
            result[path.name] = path
    if not result:
        raise FileNotFoundError(f'No {pattern} inputs in {directory}; enable --extract or supply ENDF files')
    return result


def _required(index, name):
    if name not in index:
        raise FileNotFoundError(f'Missing required evaluation: {name}')
    return index[name]


def _replacement(details, directory):
    import openmc.data

    # IAEA ZIPs contain one ENDF evaluation; do not assume its member filename.
    paths = [p for p in directory.rglob('*') if p.is_file()]
    if len(paths) != 1:
        raise ValueError(f'Expected one TENDL replacement evaluation in {directory}, found {len(paths)}')
    evaluation = openmc.data.endf.Evaluation(paths[0])
    target = evaluation.target
    if (target['atomic_number'], target['mass_number']) != details['target'] or target['isomeric_state']:
        raise ValueError(f'Wrong TENDL replacement target in {paths[0]}')
    return paths[0]


def _photon_pairs(directory):
    photo = {name[len('photoat-'):]: path for name, path in _index(directory, 'photoat-*.endf').items()}
    atom = {name[len('atom-'):]: path for name, path in _index(directory, 'atom-*.endf').items()}
    if photo.keys() != atom.keys():
        raise ValueError(f'Unpaired photon evaluations: {sorted(photo.keys() ^ atom.keys())}')
    return [(photo[key], atom[key]) for key in sorted(photo)]


def _process_task(particle, paths, output, libver, temperatures):
    """Each task has its own output directory, so name collisions cannot overwrite data."""
    output.mkdir(parents=True)
    try:
        if particle == 'neutron':
            process_neutron(paths[0], output, libver, temperatures)
        elif particle == 'thermal':
            process_thermal(*paths, output, libver)
        else:
            import openmc.data
            data = openmc.data.IncidentPhoton.from_endf(*paths)
            data.export_to_hdf5(output / f'{data.name}.h5', 'w', libver=libver)
        files = list(output.glob('*.h5'))
        if len(files) != 1 or not files[0].stat().st_size:
            raise RuntimeError(f'Expected one nonempty HDF5 output in {output}')
        return particle, files[0]
    except Exception as exc:
        raise RuntimeError(f'Failed processing {particle}: {paths}') from exc


def _generate(tasks, destination, args):
    import openmc.data

    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.jeff-generate-', dir=destination.parent) as tmp:
        staging = Path(tmp)
        work = [(particle, paths, staging / 'jobs' / str(i), args.libver, args.temperatures)
                for i, (particle, paths) in enumerate(tasks)]
        tracker = ProgressTracker(len(work), verb='Processed')
        if args.jobs == 1:
            results = []
            for task in work:
                results.append(_process_task(*task))
                tracker.complete(task[1][-1].name)
        else:
            with Pool(processes=args.jobs) as pool:
                pending = [pool.apply_async(_process_task, task,
                           callback=tracker.callback(task[1][-1].name)) for task in work]
                # get(), not wait(): any worker error aborts before publication.
                results = [result.get() for result in pending]

        library = openmc.data.DataLibrary()
        outputs = {}
        for particle, path in sorted(results, key=lambda item: (item[0], item[1].name)):
            relative = Path(particle) / path.name
            if relative in outputs:
                raise ValueError(f'Output name collision: {relative}')
            library.register_file(path)
            outputs[relative] = path
        manifest = staging / 'cross_sections.xml'
        library.export_to_xml(manifest)

        # Make paths relative to the manifest, not the temporary staging directory.
        # DataLibrary may otherwise add an absolute <directory> for single-particle runs.
        from xml.etree import ElementTree as ET
        tree = ET.parse(manifest)
        root = tree.getroot()
        directory = root.find('directory')
        if directory is not None:
            root.remove(directory)
        for entry, relative in zip(root.findall('library'), outputs):
            entry.set('path', relative.as_posix())
        tree.write(manifest, encoding='utf-8', xml_declaration=True)

        destination.mkdir(parents=True, exist_ok=True)
        # Old data remain untouched on processing/validation failure. Once publishing
        # starts, remove the old manifest so an I/O failure cannot advertise mixed data.
        (destination / 'cross_sections.xml').unlink(missing_ok=True)
        for relative, path in outputs.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            path.replace(target)
        manifest.replace(destination / 'cross_sections.xml')


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if args.jobs is not None and args.jobs < 1:
        parser.error('--jobs must be positive')
    if any(not math.isfinite(t) or t <= 0 for t in args.temperatures):
        parser.error('--temperatures must be finite and positive')
    if len({round(t) for t in args.temperatures}) != len(args.temperatures):
        parser.error('--temperatures must have distinct rounded kelvin values (OpenMC HDF5 labels)')
    particles = set(args.particles)
    required = [p for p in ('neutron', 'thermal', 'photon')
                if p in particles or (p == 'neutron' and 'thermal' in particles)]
    details = jeff_endf_details[args.release]
    destination = (args.destination or Path(f'jeff-{args.release}-hdf5')).resolve()
    archives = (args.download_dir or Path(f'jeff-{args.release}-download')).resolve()
    inputs = (args.endf_dir or Path(f'jeff-{args.release}-endf')).resolve()
    for a, b in ((destination, archives), (destination, inputs), (archives, inputs)):
        if a == b or a in b.parents or b in a.parents:
            parser.error('Destination, download and ENDF directories must not overlap')

    with ExitStack() as stack:
        if args.use_tmpdir:
            if args.download and args.extract and not args.download_dir and not args.endf_dir:
                temporary = Path(stack.enter_context(TemporaryDirectory(prefix='jeff-inputs-')))
                archives, inputs = temporary / 'download', temporary / 'endf'
            else:
                warnings.warn('--use-tmpdir ignored when reusing local inputs or explicit cache directories')
        prepared = []
        for particle in required:
            _prepare(details[particle], archives / particle, inputs / particle, args)
            prepared.append(particle)

        tasks = []
        if 'neutron' in required:
            neutrons = _index(inputs / 'neutron', details['neutron']['pattern'])
        if 'neutron' in particles:
            selected = dict(neutrons)
            if args.release == '3.3':
                for name, replacement in jeff33_replacements.items():
                    if name in selected:
                        group = 'replacements/' + Path(name).stem
                        _prepare(replacement, archives / group, inputs / group, args)
                        prepared.append(group)
                        selected[name] = _replacement(replacement, inputs / group)
                        print(f'Using TENDL-2019 replacement for {name}')
            tasks.extend(('neutron', (path,)) for path in selected.values())
        if 'thermal' in particles:
            thermal = _index(inputs / 'thermal', details['neutron']['pattern'])
            tasks.extend(('thermal', (_required(neutrons, n), _required(thermal, t)))
                         for n, t in details['thermal']['pairs'])
        if 'photon' in particles:
            tasks.extend(('photon', pair) for pair in _photon_pairs(inputs / 'photon'))
        if not tasks:
            raise ValueError('No evaluations selected for generation')
        _generate(tasks, destination, args)
        if args.cleanup:
            for group in prepared:
                for root, enabled in ((archives, args.download), (inputs, args.extract)):
                    if enabled and (root / group).exists():
                        shutil.rmtree(root / group)
    print(f'Wrote {destination / "cross_sections.xml"}')


if __name__ == '__main__':
    main()