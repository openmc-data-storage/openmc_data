"""Offline tests: never download the multi-GB production libraries."""

import argparse
import importlib.util
import io
from pathlib import Path
import shutil
import socket
import sys
import tarfile
from unittest.mock import Mock, call

import pytest

from openmc_data import utils
from openmc_data.download import download_jeff
from openmc_data.urls_h5 import all_h5_release_details


ARCHIVES = {
    "3.3": "4jwkvrr9pxlruuihcrgti75zde6g7bum.xz",
    "4.0": "fmcr8zoox1t6um0rwb2iw1nz72xue8ol.xz",
}
BASE_URL = "https://anl.box.com/shared/static/"


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("Network access and unverified size estimates are forbidden")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(utils, "urlopen", forbidden)
    monkeypatch.setattr(utils, "state_download_size", forbidden)
    monkeypatch.setattr(download_jeff, "state_download_size", forbidden, raising=False)


@pytest.fixture
def operations(monkeypatch):
    download = Mock()
    extract = Mock()
    monkeypatch.setattr(download_jeff, "download", download)
    monkeypatch.setattr(download_jeff, "extract", extract)
    return download, extract


@pytest.mark.parametrize("release", ARCHIVES)
def test_official_archive_metadata(release):
    details = all_h5_release_details["jeff"][release]["neutron-photon"]
    assert details["base_url"] == BASE_URL
    assert details["compressed_files"] == [ARCHIVES[release]]
    assert "compressed_file_size" not in details
    assert "uncompressed_file_size" not in details


def test_import_is_safe(monkeypatch, tmp_path, capsys):
    forbidden = Mock(side_effect=AssertionError("Import must not perform work"))
    monkeypatch.setattr(sys, "argv", ["unrelated-program", "--unrelated-option"])
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", forbidden)
    monkeypatch.setattr(utils, "download", forbidden)
    monkeypatch.setattr(utils, "extract", forbidden)
    spec = importlib.util.spec_from_file_location("jeff_import_test", download_jeff.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert callable(module.main)
    forbidden.assert_not_called()
    assert list(tmp_path.iterdir()) == []
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("release,options", [
    ("4.0", []), ("3.3", ["-r", "3.3"]), ("4.0", ["--release", "4.0"]),
])
@pytest.mark.parametrize("destination", [None, "relative", "absolute"])
@pytest.mark.parametrize("flags, download, extract, cleanup", [
    ([], True, True, False),
    (["--download", "--extract", "--cleanup"], True, True, True),
    (["--no-download"], False, True, False),
    (["--no-extract"], True, False, False),
    (["--no-download", "--no-extract", "--cleanup"], False, False, True),
    (["--cleanup", "--no-cleanup"], True, True, False),
    (["--no-download", "--download", "--no-extract", "--extract"], True, True, False),
    (["--download", "--no-download", "--extract", "--no-extract"], False, False, False),
])
def test_cli(operations, tmp_path, monkeypatch, release, options, destination,
             flags, download, extract, cleanup):
    root = Path("nested data/libraries") if destination else Path()
    if destination == "absolute":
        root = tmp_path / root
    argv = [*options, *flags]
    if destination:
        argv += ["-d" if destination == "relative" else "--destination", str(root)]
    monkeypatch.setattr(sys, "argv", ["download_jeff", *argv])
    download_jeff.main()  # Exercise sys.argv as well as explicit argv in other tests.
    archive = root / f"jeff-{release}-download" / ARCHIVES[release]
    assert operations[0].call_args_list == ([call(BASE_URL + archive.name, output_path=archive.parent)] if download else [])
    assert operations[1].call_args_list == ([call(
        compressed_files=[archive], extraction_dir=root / f"jeff-{release}-hdf5",
        del_compressed_file=cleanup)] if extract else [])
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("argv,code", [(["--help"], 0)] + [
    (["--release", value], 2) for value in ("3.2", "b8.1", "5.0")
])
def test_parser_exit(operations, tmp_path, capsys, argv, code):
    with pytest.raises(SystemExit) as exc:
        download_jeff.main(argv)
    assert exc.value.code == code
    output = capsys.readouterr()
    expected = ("invalid choice", "3.3", "4.0") if code else (
        "--release", "{3.3,4.0}", "--destination", "--download", "--no-download",
        "--extract", "--no-extract", "--cleanup", "--no-cleanup", "default: 4.0")
    assert all(text in (output.err if code else output.out) for text in expected)
    assert not any(mock.called for mock in operations)
    assert list(tmp_path.iterdir()) == []


@pytest.fixture
def tiny_archive(tmp_path):
    """A real tar.xz archive with small, non-nuclear-data payloads."""
    archive = tmp_path / "tiny.tar.xz"
    payloads = {
        "library/cross_sections.xml": b"<cross_sections />\n",
        "library/neutron/payload.txt": b"test payload\n",
    }
    with tarfile.open(archive, "w:xz") as tar:
        for name, contents in payloads.items():
            member = tarfile.TarInfo(name)
            member.size = len(contents)
            tar.addfile(member, io.BytesIO(contents))
    return archive, payloads


@pytest.mark.parametrize("release", ARCHIVES)
@pytest.mark.parametrize("download", [False, True])
@pytest.mark.parametrize("cleanup", [False, True])
def test_real_extraction(monkeypatch, tmp_path, tiny_archive, release, download, cleanup):
    archive, payloads = tiny_archive
    root = tmp_path / "custom" / "destination"
    download_path = root / f"jeff-{release}-download"
    compressed_file = download_path / ARCHIVES[release]

    def copy_fixture(url, output_path):
        assert url == BASE_URL + ARCHIVES[release]
        assert output_path == download_path
        output_path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive, compressed_file)
        return compressed_file

    download_mock = Mock(side_effect=copy_fixture)
    monkeypatch.setattr(download_jeff, "download", download_mock)
    if not download:
        copy_fixture(BASE_URL + ARCHIVES[release], download_path)
    download_jeff.main([
        "-r", release, "-d", str(root),
        "--download" if download else "--no-download",
        "--cleanup" if cleanup else "--no-cleanup",
    ])

    assert download_mock.call_count == int(download)
    for name, contents in payloads.items():
        assert (root / f"jeff-{release}-hdf5" / name).read_bytes() == contents
    assert compressed_file.exists() is not cleanup
    assert archive.exists()


@pytest.mark.parametrize("release", ARCHIVES)
def test_cleanup_without_extraction_keeps_archive(tmp_path, tiny_archive, release):
    archive, _ = tiny_archive
    download_path = tmp_path / f"jeff-{release}-download"
    download_path.mkdir()
    compressed_file = download_path / ARCHIVES[release]
    shutil.copyfile(archive, compressed_file)

    download_jeff.main(["-r", release, "--no-download", "--no-extract", "--cleanup"])

    assert compressed_file.read_bytes() == archive.read_bytes()
    assert not (tmp_path / f"jeff-{release}-hdf5").exists()


@pytest.mark.parametrize("release", ARCHIVES)
def test_failed_extraction_keeps_archive(tmp_path, release):
    download_path = tmp_path / f"jeff-{release}-download"
    download_path.mkdir()
    compressed_file = download_path / ARCHIVES[release]
    compressed_file.write_bytes(b"not an archive")

    with pytest.raises(tarfile.ReadError):
        download_jeff.main(["-r", release, "--no-download", "--cleanup"])

    assert compressed_file.read_bytes() == b"not an archive"


def test_failed_download_does_not_extract(operations):
    download, extract = operations
    download.side_effect = OSError("download failed")

    with pytest.raises(OSError, match="download failed"):
        download_jeff.main(["--cleanup"])

    extract.assert_not_called()