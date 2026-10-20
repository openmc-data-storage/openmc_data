"""Offline orchestration tests and opt-in real NJOY sample tests.

Offline tests use real HDF5/XML with mocked NJOY. Integration tests require
OPENMC_JEFF_INTEGRATION=1 and NJOY on PATH, and stream bounded archive samples
rather than saving complete libraries. They are not full-library qualification.
"""

from contextlib import nullcontext
import hashlib
import importlib
import os
from pathlib import Path
import sys
import tarfile
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock
import zipfile

import h5py
import numpy as np
import openmc.data
import pytest
import requests
from stream_unzip import stream_unzip

from openmc_data.generate import generate_jeff as gen
from openmc_data.urls_jeff import jeff_endf_details, jeff33_replacements


@pytest.fixture(autouse=True)
def temporary_workdir(tmp_path, monkeypatch):
    """Keep working files and temporary staging/NJOY files inside tmp_path."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tempfile, 'tempdir', str(tmp_path))
    monkeypatch.setenv('TMPDIR', str(tmp_path))


def put(path, content='input'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def hdf5(directory, name, particle):
    with h5py.File(directory / f'{name}.h5', 'w') as f:
        f.attrs['filetype'] = np.bytes_('data_' + particle)
        f.create_group(name)


def inputs(root, release):
    pairs = jeff_endf_details[release]['thermal']['pairs']
    for i, name in enumerate(sorted({n for n, _ in pairs})):
        put(root / 'neutron' / 'nested' / name, f'N{i}')
    for i, (_, name) in enumerate(pairs):
        put(root / 'thermal' / 'nested' / name, f'c_material{i}')
    for prefix in ['photoat', 'atom']:
        for z, symbol in [(1, 'H'), (8, 'O')]:
            put(root / 'photon' / prefix / f'{prefix}-{z:03}_{symbol}_000.endf', symbol)


@pytest.fixture
def processing(tmp_path, monkeypatch):
    calls = []
    def neutron(path, output, libver, temperatures):
        calls.append(('neutron', path, libver, temperatures))
        hdf5(output, path.read_text(), 'neutron')
    def thermal(path, tsl, output, libver):
        calls.append(('thermal', path, tsl, libver))
        hdf5(output, tsl.read_text(), 'thermal')
    def photon(photo, atom):
        assert photo.read_text() == atom.read_text()
        calls.append(('photon', photo, atom))
        name = photo.read_text()
        def export(path, mode, libver):
            assert mode == 'w'
            hdf5(path.parent, name, 'photon')
        return SimpleNamespace(name=name, export_to_hdf5=export)
    monkeypatch.setattr(gen, 'process_neutron', neutron)
    monkeypatch.setattr(gen, 'process_thermal', thermal)
    monkeypatch.setattr(openmc.data.IncidentPhoton, 'from_endf', photon)
    monkeypatch.setattr(gen, 'download', MagicMock(side_effect=AssertionError('Unexpected network access')))
    return calls


def offline(release, particles):
    return ['-r', release, '-p', *particles, '--jobs', '1', '--no-download', '--no-extract']


@pytest.mark.parametrize('release,count', [('3.3', 20), ('4.0', 128)])
@pytest.mark.parametrize('particles', [('neutron',), ('thermal',), ('photon',), ('neutron', 'thermal', 'photon')])
def test_release_particle_selection(tmp_path, processing, release, count, particles):
    root = tmp_path / f'jeff-{release}-endf'
    inputs(root, release)
    destination = tmp_path / f'jeff-{release}-hdf5'
    put(destination / 'neutron' / 'stale.h5', 'not HDF5')
    gen.main(offline(release, particles) + ['--temperatures', '300', '700', '--libver', 'latest'])
    library = openmc.data.DataLibrary.from_xml(destination / 'cross_sections.xml')
    assert {entry['type'] for entry in library} == set(particles)
    assert all(Path(entry['path']).is_file() for entry in library)
    assert all('stale' not in entry['path'] and '.jeff-' not in entry['path'] for entry in library)
    assert (destination / 'neutron' / 'stale.h5').read_text() == 'not HDF5'
    assert len([c for c in processing if c[0] == 'thermal']) == (count if 'thermal' in particles else 0)
    for call in processing:
        if call[0] == 'neutron':
            assert call[2:] == ('latest', [300.0, 700.0])
        if call[0] == 'thermal':
            assert len(call) == 4  # no neutron temperature override
    assert not list(tmp_path.glob('.jeff-generate-*'))


def test_defaults_and_import_safe(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['program', '--not-a-generator-option'])
    importlib.reload(gen)
    args = gen._parser().parse_args([])
    assert args.release == '4.0' and not args.use_tmpdir
    assert args.destination is None and args.libver == 'earliest'
    assert args.temperatures == [250.0, 293.6, 600.0, 900.0, 1200.0, 2500.0]
    assert args.particles == ['neutron', 'thermal', 'photon']


@pytest.mark.parametrize('argv', [
    ['-r', '3.2'], ['--jobs', '0'], ['--jobs', '-1'], ['--temperatures', '0'],
    ['--temperatures', '-5'], ['--temperatures', 'nan'], ['--temperatures', 'inf'],
    ['--temperatures', '293.6', '294'], ['-p', 'electron'],
    ['-d', 'cache/out', '--endf-dir', 'cache'],
    ['--endf-dir', 'cache', '--download-dir', 'cache/download'],
])
def test_invalid_arguments(argv, tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as error:
        gen.main(argv)
    assert error.value.code == 2
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('release', ['3.3', '4.0'])
def test_thermal_download_dependency(tmp_path, processing, monkeypatch, release):
    inputs(tmp_path / f'jeff-{release}-endf', release)
    prepare = MagicMock()
    monkeypatch.setattr(gen, '_prepare', prepare)
    gen.main(['-r', release, '-p', 'thermal', '--jobs', '1'])
    assert [call.args[2].name for call in prepare.call_args_list] == ['neutron', 'thermal']
    assert {c[0] for c in processing} == {'thermal'}
    assert not (tmp_path / f'jeff-{release}-hdf5/neutron').exists()


@pytest.mark.parametrize('problem', ['empty', 'missing_neutron', 'missing_thermal', 'duplicate'])
def test_missing_and_ambiguous_inputs(tmp_path, processing, problem):
    root = tmp_path / 'jeff-4.0-endf'
    if problem != 'empty':
        inputs(root, '4.0')
        n, t = jeff_endf_details['4.0']['thermal']['pairs'][0]
        if problem == 'missing_neutron':
            (root / 'neutron/nested' / n).unlink()
        elif problem == 'missing_thermal':
            (root / 'thermal/nested' / t).unlink()
        else:
            put(root / 'neutron/duplicate' / n)
    with pytest.raises((FileNotFoundError, ValueError)):
        gen.main(offline('4.0', ['thermal']))
    assert not processing
    assert not (tmp_path / 'jeff-4.0-hdf5/cross_sections.xml').exists()


@pytest.mark.parametrize('problem', ['missing', 'mismatch', 'duplicate'])
def test_photon_pair_validation(tmp_path, processing, problem):
    root = tmp_path / 'jeff-4.0-endf'
    inputs(root, '4.0')
    atom = root / 'photon/atom/atom-001_H_000.endf'
    if problem == 'missing':
        atom.unlink()
    elif problem == 'mismatch':
        atom.rename(atom.with_name('atom-002_He_000.endf'))
    else:
        put(root / 'photon/duplicate' / atom.name, 'H')
    with pytest.raises(ValueError):
        gen.main(offline('4.0', ['photon']))
    assert not processing


@pytest.mark.parametrize('existing', [False, True])
@pytest.mark.parametrize('failure', ['worker', 'collision', 'empty', 'invalid_hdf5'])
def test_processing_failure_never_publishes(tmp_path, processing, monkeypatch, existing, failure):
    root = tmp_path / 'jeff-4.0-endf'
    inputs(root, '4.0')
    dest = tmp_path / 'jeff-4.0-hdf5'
    if existing:
        put(dest / 'cross_sections.xml', 'old manifest')
        put(dest / 'neutron/N0.h5', 'old data')
    def broken(path, output, libver, temperatures):
        if failure == 'worker':
            raise ValueError('NJOY failed')
        if failure == 'collision':
            hdf5(output, 'same', 'neutron')
        if failure == 'invalid_hdf5':
            put(output / 'bad.h5', 'invalid')
    monkeypatch.setattr(gen, 'process_neutron', broken)
    with pytest.raises((RuntimeError, ValueError, OSError)):
        gen.main(offline('4.0', ['neutron']) + ['--cleanup'])
    if existing:
        assert (dest / 'cross_sections.xml').read_text() == 'old manifest'
        assert (dest / 'neutron/N0.h5').read_text() == 'old data'
    else:
        assert not dest.exists()
    assert root.is_dir()
    assert not list(tmp_path.glob('.jeff-generate-*'))


def test_pool_exception_is_retrieved(tmp_path, processing, monkeypatch):
    inputs(tmp_path / 'jeff-4.0-endf', '4.0')
    pool = MagicMock()
    pool.__enter__.return_value = pool
    pool.apply_async.return_value.get.side_effect = RuntimeError('remote NJOY failure')
    factory = MagicMock(return_value=pool)
    monkeypatch.setattr(gen, 'Pool', factory)
    with pytest.raises(RuntimeError, match='remote NJOY failure'):
        gen.main(offline('4.0', ['neutron']) + ['--jobs', '2'])
    factory.assert_called_once_with(processes=2)
    pool.apply_async.return_value.get.assert_called_once()
    pool.apply_async.return_value.wait.assert_not_called()
    assert not (tmp_path / 'jeff-4.0-hdf5/cross_sections.xml').exists()


@pytest.mark.parametrize('temporary', [False, True])
@pytest.mark.parametrize('failure', [False, True])
def test_input_cleanup(tmp_path, processing, monkeypatch, temporary, failure):
    root = tmp_path / 'jeff-4.0-endf'
    inputs(root, '4.0')
    archive = put(tmp_path / 'jeff-4.0-download/photon/data.zip')
    other = put(tmp_path / 'jeff-4.0-download/neutron/keep.zip')
    roots = []
    def prepare(details, archives, directory, args):
        roots.append(directory.parent)
        inputs(directory.parent, '4.0')
    monkeypatch.setattr(gen, '_prepare', prepare)
    if failure:
        monkeypatch.setattr(gen, '_generate', MagicMock(side_effect=RuntimeError('failed')))
    with pytest.raises(RuntimeError) if failure else nullcontext():
        gen.main(['-p', 'photon', '--jobs', '1', '--use-tmpdir' if temporary else '--cleanup'])
    assert roots
    assert all(path.exists() is not temporary for path in roots)
    assert archive.exists() is (temporary or failure)
    assert (root / 'photon').exists() is (temporary or failure)
    assert other.exists() and (root / 'neutron').exists()
    assert Path.cwd() == tmp_path


@pytest.mark.parametrize('release', ['3.3', '4.0'])
def test_offline_tmpdir_uses_persistent_inputs(tmp_path, processing, release):
    inputs(tmp_path / f'jeff-{release}-endf', release)
    cwd = Path.cwd()
    with pytest.warns(UserWarning, match='ignored'):
        gen.main(offline(release, ['photon']) + ['--use-tmpdir', '--cleanup'])
    assert Path.cwd() == cwd
    assert (tmp_path / f'jeff-{release}-hdf5/cross_sections.xml').is_file()
    assert (tmp_path / f'jeff-{release}-endf/photon').exists()


@pytest.mark.parametrize('download_enabled', [False, True])
def test_archive_cache_checksum_and_fresh_extraction(tmp_path, monkeypatch, download_enabled):
    archives = tmp_path / 'archives'
    archives.mkdir()
    archive = archives / 'library.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('nested/H1.jeff', 'H1')
    checksum = hashlib.md5(archive.read_bytes()).hexdigest()
    details = {'base_url': 'https://example.invalid/', 'compressed_files': ['library.zip'],
               'checksums': [checksum], 'url_suffix': '/content'}
    args = SimpleNamespace(download=download_enabled, extract=True)
    network = MagicMock(side_effect=AssertionError('Valid cache must not access network'))
    monkeypatch.setattr(gen, 'download', network)
    target = tmp_path / 'inputs'
    put(target / 'stale.jeff')
    gen._prepare(details, archives, target, args)
    assert (target / 'nested/H1.jeff').read_text() == 'H1'
    assert not (target / 'stale.jeff').exists()
    network.assert_not_called()
    archive.write_bytes(b'corrupt')
    if not download_enabled:
        with pytest.raises(OSError, match='MD5'):
            gen._prepare(details, archives, target, args)
    else:
        with pytest.raises(AssertionError, match='network'):
            gen._prepare(details, archives, target, args)
        assert network.call_args.kwargs['output_filename'] == 'library.zip'
        assert network.call_args.args[0].endswith('library.zip/content')
    assert (target / 'nested/H1.jeff').is_file()


def test_missing_archive_is_actionable(tmp_path):
    with pytest.raises(FileNotFoundError, match='enable --download'):
        gen._prepare(jeff_endf_details['4.0']['neutron'], tmp_path / 'archives',
                     tmp_path / 'inputs', SimpleNamespace(download=False, extract=True))


def test_replacements_do_not_rename_originals(tmp_path, processing, monkeypatch):
    inputs(tmp_path / 'jeff-3.3-endf', '3.3')
    for name, details in jeff33_replacements.items():
        put(tmp_path / 'jeff-3.3-endf/neutron/nested' / name, 'original')
        put(tmp_path / 'jeff-3.3-endf/replacements' / Path(name).stem / 'evaluation.dat', name[:1])
    targets = {'6': (6, 13), '8': (8, 17)}
    def evaluation(path):
        z, a = targets[path.read_text()]
        return SimpleNamespace(target={'atomic_number': z, 'mass_number': a, 'isomeric_state': 0})
    monkeypatch.setattr(openmc.data.endf, 'Evaluation', evaluation)
    gen.main(offline('3.3', ['neutron']))
    assert len([c for c in processing if c[1].suffix == '.dat']) == 2
    for name in jeff33_replacements:
        assert (tmp_path / 'jeff-3.3-endf/neutron/nested' / name).read_text() == 'original'
        assert (tmp_path / 'jeff-3.3-endf/replacements' / Path(name).stem / 'evaluation.dat').exists()


@pytest.mark.parametrize('problem', ['missing', 'multiple', 'wrong_target', 'metastable'])
def test_replacement_validation(tmp_path, monkeypatch, problem):
    details = jeff33_replacements['6-C-13g.jeff33']
    if problem != 'missing':
        put(tmp_path / 'evaluation.dat')
    if problem == 'multiple':
        put(tmp_path / 'other.dat')
    target = {'atomic_number': 8 if problem == 'wrong_target' else 6,
              'mass_number': 13, 'isomeric_state': int(problem == 'metastable')}
    monkeypatch.setattr(openmc.data.endf, 'Evaluation', lambda _: SimpleNamespace(target=target))
    with pytest.raises(ValueError):
        gen._replacement(details, tmp_path)


def test_publication_failure_removes_manifest(tmp_path, processing, monkeypatch):
    inputs(tmp_path / 'jeff-4.0-endf', '4.0')
    dest = tmp_path / 'jeff-4.0-hdf5'
    put(dest / 'cross_sections.xml', 'old manifest')
    replace = Path.replace
    def fail(path, target):
        if Path(target).parent == dest / 'photon':
            raise OSError('disk failure')
        return replace(path, target)
    monkeypatch.setattr(Path, 'replace', fail)
    with pytest.raises(OSError, match='disk failure'):
        gen.main(offline('4.0', ['photon']))
    assert not (dest / 'cross_sections.xml').exists()


def test_metadata_invariants():
    assert set(jeff_endf_details) == {'3.3', '4.0'}
    for release, count in [('3.3', 20), ('4.0', 128)]:
        details = jeff_endf_details[release]
        assert set(details) == {'neutron', 'thermal', 'photon'}
        pairs = details['thermal']['pairs']
        assert len(pairs) == len({t for n, t in pairs}) == count
        assert all(n.endswith(details['neutron']['pattern'][1:]) for n, _ in pairs)
        for group in details.values():
            assert len(group['compressed_files']) == len(group['checksums'])
            assert all(len(checksum) == 32 for checksum in group['checksums'])
        assert ('VIII.0' if release == '3.3' else 'VIII.1') in details['photon']['compressed_files'][0]
    assert ('n_8-O-016g.jeff', 'tsl_O_D20.jeff') in jeff_endf_details['4.0']['thermal']['pairs']
    assert len(jeff33_replacements) == 2


# Opt-in real NJOY samples, separate from the offline orchestration above.
class BoundedStream:
    def __init__(self, raw, limit):
        self.raw, self.limit, self.count = raw, limit, 0

    def read(self, size):
        if size < 0 or self.count + size > self.limit:
            raise RuntimeError('Archive sample exceeded its byte budget')
        data = self.raw.read(size)
        self.count += len(data)
        return data


def sample(details, wanted, destination, budget):
    """Extract named samples while streaming; close immediately after finding them."""
    name = details['compressed_files'][0]
    url = details['base_url'] + name + details.get('url_suffix', '')
    missing = set(wanted)
    destination.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, headers={'Accept-Encoding': 'identity'}, timeout=(10, 60)) as r:
        r.raise_for_status()
        stream = BoundedStream(r.raw, budget)
        if name.endswith('.zip'):
            # Delegate ZIP64, decompression, CRC and truncation checks to the reader.
            for member, _, chunks in stream_unzip(iter(lambda: stream.read(65536), b'')):
                target = Path(member.decode()).name
                if target in missing:
                    with (destination / target).open('wb') as output:
                        for chunk in chunks:
                            output.write(chunk)
                    missing.remove(target)
                    if not missing:
                        break
                else:
                    for _ in chunks:
                        pass
        else:
            with tarfile.open(fileobj=stream, mode='r|gz') as archive:
                for member in archive:
                    target = Path(member.name).name
                    if target in missing and member.isfile():
                        with archive.extractfile(member) as source:
                            (destination / target).write_bytes(source.read())
                        missing.remove(target)
                        if not missing:
                            break
        assert not missing, missing
        print(f'Sampled {name}: {stream.count} compressed bytes')


@pytest.mark.network
@pytest.mark.integration
@pytest.mark.skipif(os.environ.get('OPENMC_JEFF_INTEGRATION') != '1',
                    reason='set OPENMC_JEFF_INTEGRATION=1 for opt-in network/NJOY sample validation')
@pytest.mark.parametrize('release,particle,n,t', [
    ('3.3', 'neutron', '1-H-1g.jeff33', None),
    ('4.0', 'neutron', 'n_1-H-001g.jeff', None),
    ('3.3', 'thermal', '1-H-1g.jeff33', 'tsl-HinH2O.jeff33'),
    ('4.0', 'thermal', 'n_3-Li-007g.jeff', 'tsl_7Li_7LiD.jeff'),
    ('3.3', 'photon', None, None), ('4.0', 'photon', None, None),
])
def test_real_sample(tmp_path, release, particle, n, t):
    root = tmp_path / f'jeff-{release}-endf'
    destination = tmp_path / f'jeff-{release}-hdf5'
    details = jeff_endf_details[release]
    if n:
        sample(details['neutron'], [n], root / 'neutron', 128 * 1024**2)
    if t:
        sample(details['thermal'], [t], root / 'thermal', 40 * 1024**2)
        args = gen._parser().parse_args(['--jobs', '1', '--temperatures', '700'])
        gen._generate([('thermal', (root / 'neutron' / n, root / 'thermal' / t))], destination, args)
    else:
        if particle == 'photon':
            for archive, prefix in zip(details['photon']['compressed_files'], ['photoat', 'atom']):
                sample(dict(details['photon'], compressed_files=[archive]),
                       [f'{prefix}-001_H_000.endf'], root / 'photon', 32 * 1024**2)
        # Real neutron workers exercise child-process import safety and error transport.
        gen.main(offline(release, [particle]) + ['--temperatures', '293.6',
                                                '--jobs', '2' if n else '1'])
    outputs = list((destination / particle).glob('*.h5'))
    assert len(outputs) == 1
    if particle == 'neutron':
        data = openmc.data.IncidentNeutron.from_hdf5(outputs[0])
        assert data.name == 'H1' and '294K' in data.temperatures
    elif particle == 'thermal':
        data = openmc.data.ThermalScattering.from_hdf5(outputs[0])
        assert len(data.temperatures) > 1 and data.temperatures != ['700K']
    else:
        assert openmc.data.IncidentPhoton.from_hdf5(outputs[0]).atomic_number == 1
    assert len(openmc.data.DataLibrary.from_xml(destination / 'cross_sections.xml')) == 1