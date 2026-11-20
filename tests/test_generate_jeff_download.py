"""generate_jeff must download NEA archives as a browser, as NEA refuses urllib."""

import argparse
from unittest.mock import Mock

import pytest

pytest.importorskip("openmc")

from openmc_data.generate import generate_jeff
from openmc_data.urls_jeff import jeff_endf_details


@pytest.mark.parametrize("release", ["3.3", "4.0"])
@pytest.mark.parametrize("particle", ["neutron", "thermal"])
def test_nea_downloads_use_a_browser_user_agent(monkeypatch, tmp_path, release, particle):
    details = jeff_endf_details[release][particle]
    assert details["base_url"].startswith("https://data.oecd-nea.org/")
    download = Mock()
    monkeypatch.setattr(generate_jeff, "download", download)
    args = argparse.Namespace(download=True, extract=False)
    generate_jeff._prepare(details, tmp_path / "archives", tmp_path / "inputs", args)
    assert download.call_count == len(details["compressed_files"])
    assert all(call.kwargs["as_browser"] for call in download.call_args_list)


def test_unused_duplicate_thermal_names_are_allowed(tmp_path):
    # JEFF-4.0 has burnup split Zy4 evaluations that reuse file names
    for burnup in ("10GWdt", "20GWdt"):
        path = tmp_path / "tsl_Zy4" / "Burnup" / burnup / "tsl_Sn112_Zy4.jeff"
        path.parent.mkdir(parents=True)
        path.write_text(burnup)
    (tmp_path / "tsl_H_H2O.jeff").write_text("water")
    index = generate_jeff._index(tmp_path, "*.jeff", allow_duplicates=True)
    assert generate_jeff._required(index, "tsl_H_H2O.jeff") == tmp_path / "tsl_H_H2O.jeff"
    with pytest.raises(ValueError, match="Ambiguous input tsl_Sn112_Zy4.jeff"):
        generate_jeff._required(index, "tsl_Sn112_Zy4.jeff")
    with pytest.raises(ValueError, match="Ambiguous input"):
        generate_jeff._index(tmp_path, "*.jeff")
