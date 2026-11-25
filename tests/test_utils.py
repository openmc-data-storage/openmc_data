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


def test_add_provenance_keeps_cross_sections_readable(tmp_path):
    openmc = pytest.importorskip("openmc")
    from xml.etree import ElementTree as ET

    library = openmc.data.DataLibrary()
    library.extend([
        {"path": str(tmp_path / "neutron" / "Fe56.h5"), "type": "neutron", "materials": ["Fe56"]},
        {"path": str(tmp_path / "neutron" / "C13.h5"), "type": "neutron", "materials": ["C13"]},
        {"path": str(tmp_path / "thermal" / "c_H_in_H2O.h5"), "type": "thermal", "materials": ["c_H_in_H2O"]},
    ])
    xml = tmp_path / "cross_sections.xml"
    library.export_to_xml(xml)
    before = openmc.data.DataLibrary.from_xml(xml).libraries

    openmc_data.add_provenance(xml, "JEFF-3.3", ["Not JEFF data: 6-C-13g.jeff33 replaced with TENDL-2019"])

    text = xml.read_text()
    assert text.index("<!--") < text.index("<cross_sections")
    assert "Data source: JEFF-3.3" in text
    assert "Contents: 2 neutron, 1 thermal" in text
    assert "Not JEFF data: 6-C-13g.jeff33 replaced with TENDL-2019" in text
    assert f"openmc_data {openmc_data.__version__}" in text
    ET.parse(xml)  # still well formed
    assert openmc.data.DataLibrary.from_xml(xml).libraries == before


def test_add_provenance_rejects_text_invalid_in_xml_comment(tmp_path):
    xml = tmp_path / "cross_sections.xml"
    xml.write_text("<?xml version='1.0' encoding='utf-8'?>\n<cross_sections />\n")
    with pytest.raises(ValueError, match="XML comment"):
        openmc_data.add_provenance(xml, "JEFF-4.0", ["run with --release 4.0"])
    assert "<!--" not in xml.read_text()
