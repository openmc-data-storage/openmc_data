"""Offline JEFF regression tests using small, valid ASCII ACE tables.

The numerical readers, HDF5 writers, and XML registry are real OpenMC code.
Only archive downloads are replaced; no network or NJOY is needed.
"""

import copy
import importlib
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

import openmc.data
import pytest

from openmc_data.convert import convert_jeff as converter


RELEASES = converter.RELEASES


def write_ace(path, name, temperature):
    """Two incident energies, elastic-only neutron or discrete thermal data."""
    nxs, jxs = [0]*16, [0]*32
    if name.endswith("c"):
        xss = [1.e-11, 20., 1., 1., 0., 0., 1., 1., 0., 0., 0.]
        nxs[1:4] = [int(name.split('.')[0]), 2, 0]
        jxs[0], jxs[7] = 1, 11
    else:
        xss = [2., 1.e-9, 2.e-9, 2., 2., 1.e-9, -.5, .5, 2.e-9, -.5, .5]
        nxs[2:4] = [1, 1]
        jxs[0], jxs[2] = 1, 6
    nxs[0] = len(xss)
    kT = temperature * openmc.data.K_BOLTZMANN / 1.e6
    lines = [f"{name:>10} 1.000000 {kT:.12e} synthetic", "Offline regression fixture"]
    lines += ["1001 1.0 " + "0 0.0 "*3] + ["0 0.0 "*4]*3
    lines += [' '.join(map(str, nxs[i:i+8])) for i in (0, 8)]
    lines += [' '.join(map(str, jxs[i:i+8])) for i in (0, 8, 16, 24)]
    lines += [' '.join(f'{x:.12e}' for x in xss[i:i+4]) for i in range(0, len(xss), 4)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n')
    return path


def neutron_file(root, release, temperature, symbol="Ne", mass=20, metastable=False, encoded=False):
    z = openmc.data.ATOMIC_NUMBER[symbol]
    actual = 293.6 if temperature == "293" else float(temperature)
    if release == "3.2":
        path = root / f"ACEs_{temperature}K" / f"{symbol}{mass:03d}{'M' if metastable else ''}.ACE"
    elif release == "3.3":
        path = root / f"ace_{temperature}" / f"{z}-{symbol}-{mass}{'m' if metastable else 'g'}-{temperature}.ace"
    else:
        path = root / f"{z}-{symbol}-{mass}{'m' if metastable else 'g'}-{actual:.1f}"
    zaid = 1000*z + mass + (400 if encoded else 0)
    return write_ace(path, f"{zaid}.00c", actual)


def thermal_file(root, release, temperature=423.0, index=0, identity=None):
    if release == "3.2":
        identity = identity or f"lw{index:02d}"
        path = root / 'TSL-ACE' / f'H2O-{temperature:g}.ace'
        table = f"{identity}.32t"
    elif release == "3.3":
        identity = identity or "hh2o"
        path = root / 'ace_tsl' / f'h-h2o-{temperature:g}.ace'
        table = f"{identity}.{index:02d}t"
    else:
        identity = identity or "hh2o"
        path = root / 'data' / f'{identity}.{index:02d}_{temperature:.2f}'
        table = f"{identity}.{index:02d}t"
    return write_ace(path, table, temperature)


@pytest.fixture(autouse=True)
def offline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    catalog = copy.deepcopy(converter.all_release_details)
    # The miniature library is deliberately not the full 12-case/316-table subset.
    catalog['jeff']['4.0']['thermal']['ace'].pop('selected_cases')
    catalog['jeff']['4.0']['thermal']['ace'].pop('selected_tables')
    catalog['jeff']['3.3']['thermal']['ace'].pop('required_file_groups')
    monkeypatch.setattr(converter, 'all_release_details', catalog)
    def unexpected(*args, **kwargs):
        pytest.fail('Unexpected network access')
    monkeypatch.setattr(converter, 'download', unexpected)


def cached(release, *extra):
    return ['-r', release, '--no-download', '--no-extract', *extra]


def root_for(release):
    return Path.cwd() / f'jeff-{release}-ace'


def library(release, temperatures=('600',)):
    root = root_for(release)
    for temperature in temperatures:
        neutron_file(root, release, temperature)
    thermal_file(root, release)
    return root


@pytest.mark.parametrize('release', RELEASES)
@pytest.mark.parametrize('selected', [('600',), ('900', '600', '900')])
def test_selection_no_293_base_sorted_no_duplicates(release, selected, monkeypatch):
    root = root_for(release)
    for temp in ('600', '900', '1200'):
        neutron_file(root, release, temp)
    # An unselected corrupt cache must not even be opened.
    neutron_file(root, release, '293').write_text('corrupt cached unselected data')
    thermal_file(root, release, 600, 1)
    thermal_file(root, release, 423, 0)
    read = openmc.data.ace.get_table
    calls = []
    def record(path, name=None):
        assert name is not None  # Avoid loading a whole multi-table library.
        calls.append(Path(path))
        return read(path, name)
    monkeypatch.setattr(openmc.data.ace, 'get_table', record)
    converter.main(cached(release, '-t', *selected, '--destination', 'direct'))
    output = Path('direct')
    data = openmc.data.IncidentNeutron.from_hdf5(output / 'Ne20.h5')
    assert data.temperatures == [f'{t}K' for t in sorted(set(selected), key=float)]
    thermal = openmc.data.ThermalScattering.from_hdf5(output / 'c_H_in_H2O.h5')
    assert thermal.temperatures == ['423K', '600K']
    assert len(calls) == len(set(selected)) + 2
    library = openmc.data.DataLibrary.from_xml(output / 'cross_sections.xml')
    assert {entry['type'] for entry in library} == {'neutron', 'thermal'}
    assert all(Path(entry['path']).is_file() for entry in library)
    assert not (output / f'jeff-{release}-hdf5').exists()


@pytest.mark.parametrize('release', RELEASES)
def test_default_all_available(release):
    temperatures = converter.all_release_details['jeff'][release]['neutron']['ace']['temperatures']
    library(release, temperatures)
    argv = cached(release) if release != '4.0' else ['--no-download', '--no-extract']
    converter.main(argv)
    data = openmc.data.IncidentNeutron.from_hdf5(f'jeff-{release}-hdf5/Ne20.h5')
    assert len(data.temperatures) == len(temperatures)
    assert sorted(kT / openmc.data.K_BOLTZMANN for kT in data.kTs) == pytest.approx(
        [293.6 if t == '293' else float(t) for t in temperatures])


@pytest.mark.parametrize('release, invalid', [('3.2', '350'), ('3.3', '400'), ('4.0', '293.6')])
def test_release_temperature_validation(release, invalid, capsys):
    with pytest.raises(SystemExit, match='2'):
        converter.main(['-r', release, '-t', invalid])
    assert 'choose from' in capsys.readouterr().err
    assert not root_for(release).exists()


@pytest.mark.parametrize('release', RELEASES)
@pytest.mark.parametrize('encoded', [False, True])
def test_metastables_all_temperatures_without_mutating_cache(release, encoded):
    root = root_for(release)
    originals = {}
    for temp in ('600', '900'):
        for metastable in (False, True):
            path = neutron_file(root, release, temp, 'Am', 242, metastable, encoded and metastable)
            originals[path] = path.read_bytes()
    thermal_file(root, release)
    converter.main(cached(release, '-t', '900', '600'))
    for name, state in [('Am242', 0), ('Am242_m1', 1)]:
        data = openmc.data.IncidentNeutron.from_hdf5(f'jeff-{release}-hdf5/{name}.h5')
        assert (data.name, data.metastable, data.mass_number) == (name, state, 242)
        assert data.temperatures == ['600K', '900K']
    assert all(path.read_bytes() == content for path, content in originals.items())


@pytest.mark.parametrize('release', RELEASES)
@pytest.mark.parametrize('missing', [
    'all', 'temperature', 'nuclide', 'thermal', 'empty',
    'identity', 'bad-temperature', 'type', 'thermal-empty',
])
def test_missing_or_empty_tables_fail(release, missing):
    root = root_for(release)
    thermal_file(root, release)
    if missing != 'all':
        path = neutron_file(root, release, '600')
        if missing not in ('temperature', 'nuclide'):
            neutron_file(root, release, '900')
        if missing == 'nuclide':
            neutron_file(root, release, '600', 'O', 16)
            neutron_file(root, release, '900', 'O', 16)
        if missing == 'empty':
            path.write_text('')
        elif missing in ('identity', 'bad-temperature', 'type'):
            name, temperature = {
                'identity': ('8016.00c', 600), 'bad-temperature': ('10020.00c', 900),
                'type': ('hh2o.00t', 600),
            }[missing]
            write_ace(path, name, temperature)
    if missing == 'thermal':
        thermal_file(root, release).unlink()
    elif missing == 'thermal-empty':
        thermal_file(root, release).write_text('')
    with pytest.raises((FileNotFoundError, ValueError)):
        converter.main(cached(release, '-t', '600', '900', '--cleanup'))
    assert root.exists()
    assert not Path(f'jeff-{release}-hdf5/cross_sections.xml').exists()


@pytest.mark.parametrize('release', RELEASES)
def test_exceptions_preserve_caches_and_publish_nothing(release, monkeypatch):
    root = library(release)
    downloads = Path(f'jeff-{release}-download')
    downloads.mkdir()
    (downloads / 'keep').write_text('cache')
    def fail(*args, **kwargs):
        raise RuntimeError('broken thermal data')
    monkeypatch.setattr(openmc.data.ThermalScattering, 'from_ace', fail)
    with pytest.raises(RuntimeError, match='broken thermal'):
        converter.main(cached(release, '-t', '600', '--cleanup'))
    assert root.exists() and downloads.exists()
    assert list(Path(f'jeff-{release}-hdf5').iterdir()) == []


@pytest.mark.parametrize('release', RELEASES)
@pytest.mark.parametrize('cleanup', [False, True])
def test_download_extract_cleanup_conventions(release, cleanup, tmp_path, monkeypatch):
    source = tmp_path / 'source'
    neutron_path = neutron_file(source, release, '293')
    thermal_path = thermal_file(source, release)
    calls = []
    def download(url, *, as_browser, output_path, output_filename):
        assert as_browser is True
        assert url.endswith(f'/{output_filename}/content')
        assert output_filename != 'content'
        calls.append(url)
        output_path.mkdir(exist_ok=True)
        archive = output_path / output_filename
        path = thermal_path if len(calls) == 2 else neutron_path
        member = path.relative_to(source)
        if release == '3.2' and path == neutron_path:
            member = Path(path.name)  # New 293 K archive is flat.
        if output_filename.endswith('.zip'):
            with zipfile.ZipFile(archive, 'w') as z:
                z.write(path, str(member))
        else:
            with tarfile.open(archive, 'w:gz') as t:
                t.add(path, arcname=str(member))
        return archive
    monkeypatch.setattr(converter, 'download', download)
    with pytest.warns(UserWarning, match='multiple GB'):
        converter.main(['-r', release, '-t', '293', '--cleanup' if cleanup else '--no-cleanup'])
    assert len(calls) == 2
    assert root_for(release).exists() is not cleanup
    assert Path(f'jeff-{release}-download').exists() is not cleanup
    assert Path(f'jeff-{release}-hdf5/Ne20.h5').exists()


@pytest.mark.parametrize('release', RELEASES)
def test_missing_archive_fails(release):
    with pytest.raises(FileNotFoundError):
        converter.main(['-r', release, '-t', '600', '--no-download'])


def test_32_flat_cache_and_legacy_thermal():
    root = root_for('3.2')
    path = neutron_file(root, '3.2', '293')
    path.rename(root / path.name)
    thermal = thermal_file(root, '3.2')
    legacy = root / 'ANNEX_6_3_STLs' / 'H2O' / thermal.name
    legacy.parent.mkdir(parents=True)
    thermal.rename(legacy)
    (root / 'ACEs_293K' / 'H2O-293.ACE').write_text('redundant')
    converter.main(cached('3.2', '-t', '293'))
    assert Path('jeff-3.2-hdf5/c_H_in_H2O.h5').exists()


def test_40_numeric_temperatures_and_uo2_twins():
    root = root_for('4.0')
    for temp in ('0.1', '293', '300'):
        neutron_file(root, '4.0', temp, 'H', 1)
    for index, temp in enumerate((1201., 300., 301., 1200.)):
        thermal_file(root, '4.0', temp, index, 'ouo2')
    (root / 'data' / 'directory').write_text('ignore')
    converter.main(cached('4.0', '-t', '300', '293', '0.1'))
    data = openmc.data.IncidentNeutron.from_hdf5('jeff-4.0-hdf5/H1.h5')
    assert data.temperatures == ['0K', '294K', '300K']
    data = openmc.data.ThermalScattering.from_hdf5('jeff-4.0-hdf5/c_O_in_UO2.h5')
    assert sorted(kT / openmc.data.K_BOLTZMANN for kT in data.kTs) == pytest.approx([300, 301, 1200, 1201])


@pytest.mark.parametrize('collision', ['neutron', 'thermal', 'rounded', 'existing', 'xml'])
def test_output_collisions(collision):
    root = library('4.0')
    path = neutron_file(root, '4.0', '600')
    if collision == 'neutron':
        duplicate = root / 'duplicate' / path.name
        duplicate.parent.mkdir()
        duplicate.write_bytes(path.read_bytes())
    elif collision == 'thermal':
        thermal_file(root, '4.0', 600, 1, 'lwtr')
    elif collision == 'rounded':
        thermal_file(root, '4.0', 423.1, 1, 'hh2o')
    else:
        output = Path('jeff-4.0-hdf5')
        output.mkdir()
        (output / ('Ne20.h5' if collision == 'existing' else 'cross_sections.xml')).write_text('keep')
    with pytest.raises((ValueError, FileExistsError), match='Duplicate|collision|overwrite'):
        converter.main(cached('4.0', '-t', '600'))


def test_unknown_thermal_identity_not_fuzzy_matched():
    with pytest.warns(UserWarning, match='without fuzzy matching'):
        assert converter._thermal_name('hh2onew') == 'c_hh2onew'


@pytest.mark.parametrize('field, expected', [('selected_cases', 12), ('selected_tables', 316)])
def test_incomplete_40_subset_fails(field, expected):
    library('4.0')
    converter.all_release_details['jeff']['4.0']['thermal']['ace'][field] = expected
    with pytest.raises(ValueError, match='Incomplete'):
        converter.main(cached('4.0', '-t', '600'))


@pytest.mark.parametrize('release', RELEASES)
def test_destination_in_cache_rejected(release):
    with pytest.raises(SystemExit, match='2'):
        converter.main(cached(release, '--destination', str(root_for(release) / 'out')))


@pytest.mark.parametrize('module, release, libver', [
    ('convert_jeff32', '3.2', 'latest'), ('convert_jeff33', '3.3', 'earliest')])
def test_alias_defaults_and_release_handling(module, release, libver, monkeypatch):
    alias = importlib.import_module(f'openmc_data.convert.{module}')
    temperatures = converter.all_release_details['jeff'][release]['neutron']['ace']['temperatures']
    library(release, temperatures)
    export = openmc.data.IncidentNeutron.export_to_hdf5
    versions = []
    def record(self, *args, **kwargs):
        versions.append(kwargs['libver'])
        return export(self, *args, **kwargs)
    monkeypatch.setattr(openmc.data.IncidentNeutron, 'export_to_hdf5', record)
    alias.main(['--no-download', '--no-extract'])
    alias.main(['--no-download', '--no-extract', '-r', release, '-t', '600', '-d', 'explicit', '--libver', 'earliest'])
    assert versions == [libver, 'earliest']
    with pytest.raises(SystemExit, match='2'):
        alias.main(['-r', '4.0'])


@pytest.mark.parametrize('module', ['convert_jeff', 'convert_jeff32', 'convert_jeff33'])
def test_import_safe_and_module_help(module):
    code = f"import sys; sys.argv = ['unrelated', '--invalid']; import openmc_data.convert.{module}"
    # The fixture changes cwd; a relative PYTHONPATH would otherwise import an
    # unrelated installed checkout in these child processes.
    env = {**os.environ, 'PYTHONPATH': str(Path(converter.__file__).resolve().parents[2])}
    subprocess.run([sys.executable, '-c', code], check=True, capture_output=True, text=True, env=env)
    result = subprocess.run([sys.executable, '-m', f'openmc_data.convert.{module}', '--help'],
                            check=True, capture_output=True, text=True, env=env)
    assert '--temperatures' in result.stdout


def test_ace_catalog_integrity():
    from openmc_data.urls import all_release_details
    for release in RELEASES:
        sources = all_release_details['jeff'][release]
        neutron = sources['neutron']['ace']
        assert len(neutron['compressed_files']) == len(neutron['temperatures'])
        for source in sources.values():
            ace = source['ace']
            assert ace['base_url'].startswith('https://data.oecd-nea.org/api/records/')
            assert ace['url_suffix'] == '/content'
            assert ace['as_browser'] is True
    assert 'JEFF32-ACE-800K.tar.gz' in all_release_details['jeff']['3.2']['neutron']['ace']['compressed_files']
    assert 'JEFF32-ACE-300K.tar.gz' in all_release_details['jeff']['3.2']['neutron']['ace']['compressed_files']
    subset = all_release_details['jeff']['4.0']['thermal']['ace']
    assert (subset['selected_cases'], subset['selected_tables']) == (12, 316)


def test_33_missing_material_does_not_reuse_previous_data():
    library('3.3')
    converter.all_release_details['jeff']['3.3']['thermal']['ace']['required_file_groups'] = ['h-h2o', 'be']
    with pytest.raises(FileNotFoundError, match='thermal materials: be'):
        converter.main(cached('3.3', '-t', '600'))
    assert not Path('jeff-3.3-hdf5/cross_sections.xml').exists()


def test_33_thermal_prefixes_allow_phase_suffixes():
    root = root_for('3.3')
    write_ace(root / 'ace_tsl/mesi-phii-20.ace', 'mesi.00t', 20)
    write_ace(root / 'ace_tsl/tolue-phii-20.ace', 'tol.00t', 20)
    details = {'ace_paths': ['ace_tsl/*.ace'], 'required_file_groups': ['mesi', 'tolu']}
    groups = converter._thermal_groups(root, '3.3', details)
    assert set(groups) == {'c_H_in_Mesitylene', 'c_H_in_Toluene'}


@pytest.mark.parametrize('release', RELEASES)
def test_download_without_extract_uses_cache(release, monkeypatch):
    library(release)
    downloads = []
    monkeypatch.setattr(converter, 'download', lambda *args, **kwargs: downloads.append(kwargs['output_filename']))
    def fail(*args, **kwargs):
        pytest.fail('Extraction was disabled')
    monkeypatch.setattr(converter, 'extract', fail)
    with pytest.warns(UserWarning, match='multiple GB'):
        converter.main(['-r', release, '-t', '600', '--download', '--no-extract'])
    assert len(downloads) == 2


def test_new_style_header():
    path = Path('modern.ace')
    kT = 293.6 * openmc.data.K_BOLTZMANN / 1.e6
    path.write_text(f'2.0.0 1001.40c\n1.0 {kT} date 3\ncomment\n')
    name, temperature = converter._header(path)
    assert name == '1001.40c'
    assert temperature == pytest.approx(293.6)


@pytest.mark.parametrize('problem', ['unsafe-name', 'lost-temperature', 'wrong-name'])
def test_output_safety_checks(problem, monkeypatch):
    library('3.3', ('600', '900'))
    if problem == 'unsafe-name':
        monkeypatch.setattr(converter, '_thermal_name', lambda _: '../unsafe')
    elif problem == 'lost-temperature':
        monkeypatch.setattr(openmc.data.IncidentNeutron, 'add_temperature_from_ace', lambda *a, **k: None)
    else:
        read = openmc.data.IncidentNeutron.from_ace
        def wrong(*args, **kwargs):
            data = read(*args, **kwargs)
            data.name = 'wrong'
            return data
        monkeypatch.setattr(openmc.data.IncidentNeutron, 'from_ace', wrong)
    with pytest.raises(ValueError, match='Unsafe|lost temperatures|does not match'):
        converter.main(cached('3.3', '-t', '600', '900'))
    assert not Path('jeff-3.3-hdf5/cross_sections.xml').exists()