#!/usr/bin/env python3

"""
Download JENDL data from JAEA and convert it to a HDF5 library for
use with OpenMC.
"""

import argparse
import ssl
from multiprocessing import Pool
from pathlib import Path
from urllib.parse import urljoin

import openmc.data
from openmc_data import apply_updates, download, extract, process_neutron, process_thermal, state_download_size, all_release_details, ProgressTracker


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=CustomFormatter
    )
    parser.add_argument('-d', '--destination', type=Path, default=None,
                        help='Directory to create new library in')
    parser.add_argument('--download', action='store_true',
                        help='Download files')
    parser.add_argument('--no-download', dest='download', action='store_false',
                        help='Do not download files')
    parser.add_argument('--extract', action='store_true',
                        help='Extract tar/zip files')
    parser.add_argument('--no-extract', dest='extract', action='store_false',
                        help='Do not extract tar/zip files')
    parser.add_argument('--libver', choices=['earliest', 'latest'],
                        default='latest', help="Output HDF5 versioning. Use "
                        "'earliest' for backwards compatibility or 'latest' for "
                        "performance")
    parser.add_argument('-r', '--release', choices=['4.0', '5.0'], default='4.0',
                        help="The nuclear data library release version. "
                        "The options currently supported are 4.0 and 5.0")
    parser.add_argument('-p', '--particles', choices=['neutron', 'thermal', 'photon'],
                        nargs='+', default=None,
                        help="Data to include. Defaults to everything available "
                        "for the release. Thermal scattering and photon data are "
                        "available for release 5.0. Thermal scattering also needs "
                        "the neutron evaluations, which are downloaded and "
                        "extracted when thermal is selected")
    parser.add_argument('--cleanup', action='store_true',
                        help="Remove download directories when data has "
                        "been processed")
    parser.add_argument('--no-cleanup', dest='cleanup', action='store_false',
                        help="Do not remove download directories when data has "
                        "been processed")
    parser.add_argument('--temperatures', type=float,
                        default=[250.0, 293.6, 600.0, 900.0, 1200.0, 2500.0],
                        help="Temperatures in Kelvin", nargs='+')
    parser.set_defaults(download=True, extract=True, cleanup=False)
    return parser.parse_args(argv)


def photon_pairs(photo_files, atom_files):
    """Pair photo-atomic and atomic relaxation evaluations by atomic number

    The pairing reads the target of each evaluation rather than relying on
    the two sublibraries using matching file names.
    """
    def by_atomic_number(files, description):
        evaluations = {}
        for path in files:
            z = openmc.data.endf.Evaluation(path).target['atomic_number']
            if z in evaluations:
                raise ValueError(f'Two {description} evaluations for Z={z}: '
                                 f'{evaluations[z]} and {path}')
            evaluations[z] = path
        if not evaluations:
            raise FileNotFoundError(f'No {description} evaluations found')
        return evaluations

    photo = by_atomic_number(photo_files, 'photo-atomic')
    atom = by_atomic_number(atom_files, 'atomic relaxation')
    missing = sorted(photo.keys() - atom.keys())
    if missing:
        raise FileNotFoundError(f'No atomic relaxation evaluations for Z={missing}')
    return [(photo[z], atom[z]) for z in sorted(photo)]


def main(argv=None):
    args = parse_args(argv)

    library_name = 'jendl'

    cwd = Path.cwd()

    endf_files_dir = cwd.joinpath('-'.join([library_name, args.release, 'endf']))
    download_path = cwd.joinpath('-'.join([library_name, args.release, 'download']))
    # the destination is decided after the release is known
    # to avoid putting the release in a folder with a misleading name
    if args.destination is None:
        args.destination = Path('-'.join([library_name, args.release, 'hdf5']))

    # This dictionary contains all the unique information about each release.
    # This can be exstened to accommodated new releases
    release_details = all_release_details[library_name][args.release]
    particles = args.particles or list(release_details)
    for particle in particles:
        if particle not in release_details:
            raise ValueError(f'JENDL-{args.release} has no {particle} data, '
                             f'available: {", ".join(release_details)}')
    details = {particle: release_details[particle]['endf'] for particle in particles}
    # thermal scattering is processed together with the neutron evaluations of
    # its principal scatterer, so their files are needed even if not processed
    archives = dict(details)
    if 'thermal' in details:
        archives.setdefault('neutron', release_details['neutron']['endf'])

    # ==============================================================================
    # DOWNLOAD FILES FROM WEBSITE

    if args.download:
        state_download_size(
            sum(d['compressed_file_size'] for d in archives.values()),
            sum(d['uncompressed_file_size'] for d in archives.values()),
            'GB')
        for d in archives.values():
            checksums = dict(zip(d['compressed_files'], d.get('checksums', [])))
            for f in d['compressed_files'] + d.get('updates', []):
                # Establish connection to URL
                download(
                    urljoin(d['base_url'], f),
                    checksum=checksums.get(f),
                    context=ssl._create_unverified_context(),
                    output_path=download_path
                )

    # ==============================================================================
    # EXTRACT FILES FROM TGZ
    if args.extract:
        if 'neutron' in archives:
            neutron = archives['neutron']
            extract(
                compressed_files=[download_path / f for f in neutron['compressed_files']],
                extraction_dir=endf_files_dir,
                del_compressed_file=args.cleanup
            )
            update_archives = [download_path / f for f in neutron.get('updates', [])]
            apply_updates(update_archives,
                          (endf_files_dir / neutron['endf_files']).parent)
            if args.cleanup:
                for archive in update_archives:
                    archive.unlink(missing_ok=True)
        if 'thermal' in details:
            extract(
                compressed_files=[download_path / f for f in details['thermal']['compressed_files']],
                extraction_dir=endf_files_dir,
                del_compressed_file=args.cleanup
            )
        if 'photon' in details:
            extract(
                compressed_files=[download_path / f for f in details['photon']['compressed_files']],
                extraction_dir=endf_files_dir / 'photon',
                del_compressed_file=args.cleanup
            )

    # Create output directory if it doesn't exist
    args.destination.mkdir(parents=True, exist_ok=True)

    library = openmc.data.DataLibrary()

    # ==============================================================================
    # GENERATE HDF5 LIBRARY -- NEUTRON FILES

    if 'neutron' in details:
        # Get a list of all ENDF files
        neutron_files = endf_files_dir.glob(details['neutron']['endf_files'])

        with Pool() as pool:
            results = []
            neutron_files = sorted(neutron_files)
            tracker = ProgressTracker(len(neutron_files), verb='Processed')
            for filename in neutron_files:
                func_args = (filename, args.destination, args.libver, args.temperatures)
                r = pool.apply_async(
                    process_neutron, func_args,
                    callback=tracker.callback(filename.name),
                    error_callback=tracker.callback(filename.name),
                )
                results.append(r)

            for r in results:
                r.wait()

        # Register with library
        for p in sorted((args.destination).glob('*.h5')):
            library.register_file(p)

    # ==============================================================================
    # GENERATE HDF5 LIBRARY -- THERMAL SCATTERING FILES

    if 'thermal' in details:
        thermal_files = [
            (endf_files_dir / neutron, endf_files_dir / thermal, name)
            for neutron, thermal, name in details['thermal']['sab_files']
        ]
        missing = [str(path) for pair in thermal_files for path in pair[:2]
                   if not path.is_file()]
        if missing:
            raise FileNotFoundError('Thermal scattering needs these files: '
                                    + ', '.join(sorted(set(missing))))
        thermal_destination = args.destination / 'thermal'
        thermal_destination.mkdir(parents=True, exist_ok=True)

        with Pool() as pool:
            results = []
            tracker = ProgressTracker(len(thermal_files), verb='Processed')
            for neutron, thermal, name in thermal_files:
                func_args = (neutron, thermal, thermal_destination, args.libver, name)
                r = pool.apply_async(
                    process_thermal, func_args,
                    callback=tracker.callback(name),
                    error_callback=tracker.callback(name),
                )
                results.append(r)

            for r in results:
                r.wait()

        for p in sorted(thermal_destination.glob('*.h5')):
            library.register_file(p)

    # ==============================================================================
    # GENERATE HDF5 LIBRARY -- PHOTON FILES

    if 'photon' in details:
        photon_dir = endf_files_dir / 'photon'
        pairs = photon_pairs(photon_dir.glob(details['photon']['photo_files']),
                             photon_dir.glob(details['photon']['atom_files']))
        photon_destination = args.destination / 'photon'
        photon_destination.mkdir(parents=True, exist_ok=True)
        tracker = ProgressTracker(len(pairs))
        for photo_path, atom_path in pairs:
            tracker.starting(f'{photo_path.name} {atom_path.name}')
            data = openmc.data.IncidentPhoton.from_endf(photo_path, atom_path)
            h5_file = photon_destination / f'{data.name}.h5'
            data.export_to_hdf5(h5_file, 'w', libver=args.libver)
            library.register_file(h5_file)

    # Write cross_sections.xml
    library.export_to_xml(args.destination / 'cross_sections.xml')


if __name__ == '__main__':
    main()
