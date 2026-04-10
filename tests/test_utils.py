import tarfile

import openmc_data


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
