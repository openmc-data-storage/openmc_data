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
    assert set(all_release_details["jendl"]["5.0"]) == {"neutron", "photon"}
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
