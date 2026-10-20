import tarfile

import pytest

import openmc_data
from openmc_data import utils


def test_extract_deletes_compressed_files(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    payload = source_dir / "payload.txt"
    payload.write_text("payload")

    archive = tmp_path / "payload.tar.gz"
    with tarfile.open(archive, "w:gz") as tgz:
        tgz.add(payload, arcname=payload.name)

    extraction_dir = tmp_path / "extracted"
    openmc_data.extract(archive, extraction_dir, del_compressed_file=True, verbose=False)

    assert (extraction_dir / "payload.txt").read_text() == "payload"
    assert not archive.exists()


def test_process_neutron_requires_openmc():
    if utils.openmc is not None:
        pytest.skip("openmc is installed in this environment")

    with pytest.raises(ModuleNotFoundError, match="openmc is required"):
        openmc_data.process_neutron("dummy.endf", "out", "latest")
