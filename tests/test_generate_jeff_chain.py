"""Offline tests for generate_jeff_chain: nothing is downloaded."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from openmc_data import all_decay_release_details
from openmc_data.depletion import generate_jeff_chain


def record(text, mat, mf, mt):
    return f"{text:<66}{mat:4d}{mf:2d}{mt:3d}{0:5d}\n"


def material(mat):
    # A minimal material: one section that the ENDF reader keeps as text.
    return (record(" 1.000000+0", mat, 1, 999) + record("", mat, 1, 0)
            + record("", mat, 0, 0) + record("", 0, 0, 0))


TAPE = material(9228) + material(9437) + record("", -1, 0, 0)
TPID = record(" TAPE IDENTIFIER", 1, 0, 0)


def test_release_options():
    assert set(generate_jeff_chain.RELEASES) == {"3.3", "4.0"}
    assert generate_jeff_chain.parse_args([]).release == "4.0"
    assert generate_jeff_chain.parse_args(["-r", "3.3"]).release == "3.3"
    with pytest.raises(SystemExit):
        generate_jeff_chain.parse_args(["-r", "3.2"])


@pytest.mark.parametrize("release", ["3.3", "4.0"])
def test_registry(release):
    details = all_decay_release_details["jeff"][release]
    for file_type in ("neutron", "decay", "nfy"):
        entry = details[file_type]
        assert len(entry["base_url"]) == len(entry["compressed_files"]) == len(entry["checksums"])
        assert entry["base_url"][0].startswith("https://data.oecd-nea.org/api/records/")
    assert "endf_files" in details["neutron"]


def test_tape_id_added_when_missing(tmp_path):
    path = tmp_path / "nfy.txt"
    path.write_text(TAPE)
    fixed = generate_jeff_chain.with_tape_id(path)
    assert fixed == tmp_path / "nfy-fixed.txt"
    assert fixed.read_text()[len(TPID):] == TAPE
    assert fixed.read_text()[70:75] == " 0  0"
    assert path.read_text() == TAPE


def test_tape_id_kept_when_present(tmp_path):
    path = tmp_path / "decay.txt"
    path.write_text(TPID + TAPE)
    assert generate_jeff_chain.with_tape_id(path) == path
    assert not (tmp_path / "decay-fixed.txt").exists()


@pytest.mark.filterwarnings("ignore:MF=1, MT=999 ignored")
@pytest.mark.parametrize("header", ["", TPID])
def test_tapes_split_into_every_material(tmp_path, header):
    path = tmp_path / "tape.txt"
    path.write_text(header + TAPE)
    assert [m.MAT for m in generate_jeff_chain.materials([path])] == [9228, 9437]


@pytest.mark.parametrize("release", ["3.3", "4.0"])
def test_main_builds_chain_from_all_materials(monkeypatch, tmp_path, release):
    monkeypatch.chdir(tmp_path)
    details = all_decay_release_details["jeff"][release]
    download_dir = tmp_path / f"jeff-{release}-download"
    neutron_file = tmp_path / f"jeff-{release}-endf" / "neutrons" / ("n" + details["neutron"]["endf_files"][1:])

    def download(url, checksum, as_browser, output_path, output_filename):
        path = Path(output_path) / output_filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TAPE)
        return path

    def extract(compressed_file, extraction_dir):
        neutron_file.parent.mkdir(parents=True, exist_ok=True)
        neutron_file.write_text(TAPE)

    download = Mock(side_effect=download)
    from_endf = Mock()
    monkeypatch.setattr(generate_jeff_chain, "download", download)
    monkeypatch.setattr(generate_jeff_chain, "extract", Mock(side_effect=extract))
    monkeypatch.setattr(generate_jeff_chain.openmc.deplete.Chain, "from_endf", from_endf)
    monkeypatch.setattr(generate_jeff_chain, "materials",
                        lambda paths: [p.name for p in paths])

    generate_jeff_chain.main(["-r", release])

    urls = [c.kwargs["url"] for c in download.call_args_list]
    expected = [details[t]["base_url"][0] + details[t]["compressed_files"][0] + "/content"
                for t in ("neutron", "decay", "nfy")]
    assert urls == expected
    assert all(c.kwargs["as_browser"] for c in download.call_args_list)
    kwargs = from_endf.call_args.kwargs
    assert kwargs["neutron_files"] == [neutron_file]
    assert kwargs["decay_files"] == details["decay"]["compressed_files"]
    assert kwargs["fpy_files"] == details["nfy"]["compressed_files"]
    from_endf.return_value.export_to_xml.assert_called_once_with(f"chain_jeff_{release}.xml")
