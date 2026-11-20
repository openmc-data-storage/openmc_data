"""Offline tests for generate_jendl: nothing is downloaded or processed."""

from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("openmc")

from openmc_data import all_release_details
from openmc_data.generate import generate_jendl


@pytest.fixture
def atomic_numbers(monkeypatch):
    """Read the atomic number from the file contents instead of ENDF data."""
    def evaluation(path):
        return SimpleNamespace(target={"atomic_number": int(Path(path).read_text())})
    monkeypatch.setattr(generate_jendl.openmc.data.endf, "Evaluation", evaluation)


def write(directory, files):
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, z in files.items():
        path = directory / name
        path.write_text(str(z))
        paths.append(path)
    return paths


def test_particles_default_to_release_contents():
    assert generate_jendl.parse_args([]).particles is None
    assert generate_jendl.parse_args(["-p", "photon"]).particles == ["photon"]
    assert set(all_release_details["jendl"]["5.0"]) == {"neutron", "thermal", "photon"}
    assert set(all_release_details["jendl"]["4.0"]) == {"neutron"}


def test_photon_unavailable_for_jendl4(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="JENDL-4.0 has no photon data"):
        generate_jendl.main(["-r", "4.0", "-p", "photon"])
    assert not list(tmp_path.iterdir())


def test_photon_pairs_match_atomic_number_not_file_name(tmp_path, atomic_numbers):
    photo = write(tmp_path / "pa", {"a.dat": 92, "b.dat": 1, "c.dat": 26})
    atom = write(tmp_path / "ar", {"z.dat": 1, "y.dat": 26, "x.dat": 92, "w.dat": 3})
    pairs = generate_jendl.photon_pairs(photo, atom)
    assert [(p.name, a.name) for p, a in pairs] == [
        ("b.dat", "z.dat"), ("c.dat", "y.dat"), ("a.dat", "x.dat")]


def test_photon_without_relaxation_fails(tmp_path, atomic_numbers):
    photo = write(tmp_path / "pa", {"a.dat": 1, "b.dat": 92})
    atom = write(tmp_path / "ar", {"x.dat": 92})
    with pytest.raises(FileNotFoundError, match=r"Z=\[1\]"):
        generate_jendl.photon_pairs(photo, atom)


def test_duplicate_atomic_number_fails(tmp_path, atomic_numbers):
    photo = write(tmp_path / "pa", {"a.dat": 92, "b.dat": 92})
    atom = write(tmp_path / "ar", {"x.dat": 92})
    with pytest.raises(ValueError, match="Two photo-atomic evaluations for Z=92"):
        generate_jendl.photon_pairs(photo, atom)


def test_no_photon_files_fails(tmp_path, atomic_numbers):
    with pytest.raises(FileNotFoundError, match="No photo-atomic"):
        generate_jendl.photon_pairs([], [])


def test_jendl5_photon_registry():
    details = all_release_details["jendl"]["5.0"]["photon"]["endf"]
    assert details["compressed_files"] == ["jendl5-pa.tar.gz", "jendl5-ar.tar.gz"]
    assert len(details["checksums"]) == len(details["compressed_files"])
    assert details["photo_files"] == "jendl5-pa/*.dat"
    assert details["atom_files"] == "jendl5-ar/*.dat"


def test_jendl5_thermal_registry():
    from openmc.data.njoy import _THERMAL_DATA
    details = all_release_details["jendl"]["5.0"]["thermal"]["endf"]
    pairs = details["sab_files"]
    assert details["compressed_files"] == ["jendl5-tsl.tar.gz"]
    assert len(details["checksums"]) == 1
    assert len(pairs) == 62
    # every file and name once, so no table overwrites another
    assert len({thermal for _, thermal, _ in pairs}) == 62
    assert len({name for _, _, name in pairs}) == 62
    for neutron, thermal, name in pairs:
        assert neutron.startswith("jendl5-n/n_") and thermal.startswith("jendl5-tsl/tsl_")
        assert name in _THERMAL_DATA, name


@pytest.mark.parametrize("thermal, name", [
    ("jendl5-tsl/tsl_CinLiquidToluene.dat", "c_C_in_C7H8_liquid"),
    ("jendl5-tsl/tsl_HinSolidToluene.dat", "c_H_in_C7H8_solid"),
    ("jendl5-tsl/tsl_HinLiquidBenzene.dat", "c_H_in_C6H6_liquid"),
])
def test_phases_and_elements_get_their_own_names(thermal, name):
    # OpenMC fuzzy matches these labels to one shared, and partly wrong, name
    pairs = all_release_details["jendl"]["5.0"]["thermal"]["endf"]["sab_files"]
    assert {t: n for _, t, n in pairs}[thermal] == name


def test_process_thermal_uses_the_given_name(monkeypatch, tmp_path):
    from openmc_data import utils
    calls = {}

    class Data:
        name = "c_H_in_C7H8_solid"   # the fuzzy match for C in liquid toluene
        def export_to_hdf5(self, path, mode, libver):
            calls["path"] = path

    def from_njoy(neutron, thermal, **kwargs):
        calls["kwargs"] = kwargs
        return Data()

    monkeypatch.setattr(utils.openmc.data.ThermalScattering, "from_njoy", from_njoy)
    utils.process_thermal("n.dat", "tsl.dat", tmp_path, "latest", "c_C_in_C7H8_liquid")
    assert calls["kwargs"] == {"table_name": "tolliq", "zaids": [6000, 6012, 6013], "nmix": 1}
    assert calls["path"] == tmp_path / "c_C_in_C7H8_liquid.h5"


def test_thermal_alone_also_fetches_the_neutron_evaluations(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    downloaded = []
    monkeypatch.setattr(generate_jendl, "download",
                        lambda url, **kwargs: downloaded.append(url.rsplit("/", 1)[-1]))
    monkeypatch.setattr(generate_jendl, "state_download_size", lambda *a: None)
    monkeypatch.setattr(generate_jendl, "extract", lambda **kwargs: None)
    monkeypatch.setattr(generate_jendl, "apply_updates", lambda *a: None)
    # nothing was really extracted, so it stops before running NJOY
    with pytest.raises(FileNotFoundError, match="tsl_HinH2O.dat"):
        generate_jendl.main(["-r", "5.0", "-p", "thermal"])
    neutron = all_release_details["jendl"]["5.0"]["neutron"]["endf"]
    assert downloaded == ["jendl5-tsl.tar.gz"] + neutron["compressed_files"] + neutron["updates"] or \
        downloaded == neutron["compressed_files"] + neutron["updates"] + ["jendl5-tsl.tar.gz"]
