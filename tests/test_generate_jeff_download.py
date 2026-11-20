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
