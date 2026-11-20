"""Offline tests for overlaying evaluation updates onto an extracted library."""

import io
import re
import tarfile

import pytest

from openmc_data import all_decay_release_details, all_release_details, apply_updates


def make_archive(path, files):
    with tarfile.open(path, "w:gz") as tar:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return path


@pytest.fixture
def library(tmp_path):
    target = tmp_path / "endf" / "jendl5-n"
    target.mkdir(parents=True)
    for name in ("n_001-H-002.dat", "n_026-Fe-057.dat", "n_045-Rh-101m1.dat"):
        (target / name).write_text("original")
    return target


def test_updates_replace_files_and_later_updates_win(tmp_path, library):
    first = make_archive(tmp_path / "upd1.tar.gz", {
        "upd1/n_026-Fe-057.dat": "upd1",          # nested in a directory
        "upd1/n_001-H-002.dat": "upd1",
    })
    second = make_archive(tmp_path / "upd2.tar.gz", {
        "n_026-Fe-057.dat": "upd2",               # flat, as in jendl5-n_upd17
        "n_045-Rh-101m1.dat": "upd2",
    })
    apply_updates([first, second], library)
    assert (library / "n_001-H-002.dat").read_text() == "upd1"
    assert (library / "n_026-Fe-057.dat").read_text() == "upd2"
    assert (library / "n_045-Rh-101m1.dat").read_text() == "upd2"
    assert sorted(p.name for p in library.parent.iterdir()) == ["jendl5-n"]


def test_update_order_is_respected(tmp_path, library):
    first = make_archive(tmp_path / "upd1.tar.gz", {"n_026-Fe-057.dat": "upd1"})
    second = make_archive(tmp_path / "upd2.tar.gz", {"n_026-Fe-057.dat": "upd2"})
    apply_updates([second, first], library)
    assert (library / "n_026-Fe-057.dat").read_text() == "upd1"


def test_update_for_unknown_evaluation_fails(tmp_path, library):
    archive = make_archive(tmp_path / "upd.tar.gz", {"n_099-Es-999.dat": "new"})
    with pytest.raises(FileNotFoundError, match="n_099-Es-999.dat"):
        apply_updates([archive], library)


def test_update_without_evaluations_fails(tmp_path, library):
    archive = make_archive(tmp_path / "upd.tar.gz", {"README": "nothing"})
    with pytest.raises(FileNotFoundError, match="No"):
        apply_updates([archive], library)


def test_no_updates_is_a_no_op(library):
    apply_updates([], library)
    assert all(p.read_text() == "original" for p in library.iterdir())


@pytest.mark.parametrize("details", [
    all_release_details["jendl"]["5.0"]["neutron"]["endf"],
    all_decay_release_details["jendl"]["5.0"]["neutron"],
], ids=["generate", "chain"])
def test_jendl5_updates_are_in_release_order(details):
    numbers = [int(re.fullmatch(r"jendl5-n_upd(\d+)\.tar\.gz", f)[1])
               for f in details["updates"]]
    assert numbers == sorted(numbers) == [1, 6, 7, 10, 11, 12, 14, 17]
    assert details["compressed_files"] == ["jendl5-n.tar.gz"]
    assert "errata" not in details
