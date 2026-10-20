
import time
from pathlib import Path
from unittest.mock import MagicMock
from urllib.parse import urlsplit

import pytest
import requests

from openmc_data import (
    all_release_details,
    all_h5_release_details,
    all_chain_release_details,
    all_decay_release_details,
)


# urls that serve a file kept in this repository, see check_url
REPO_RAW_PREFIX = "https://github.com/openmc-data-storage/openmc_data/raw/main/"
REPO_ROOT = Path(__file__).resolve().parent.parent
UNTESTED_URL = "https://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-endf.zip"


def validate_url(url):
    """Check registry syntax and repository files without making HTTP requests."""
    assert isinstance(url, str) and url, f"Expected a nonempty URL, got {url!r}"
    assert not any(char.isspace() for char in url), f"{url!r} contains whitespace"
    parsed = urlsplit(url)
    assert parsed.scheme in ('http', 'https'), f"{url!r} must use HTTP or HTTPS"
    assert parsed.hostname, f"{url!r} has no hostname"
    assert parsed.path and not parsed.path.endswith('/'), f"{url!r} has no file path"

    if url.startswith(REPO_RAW_PREFIX):
        relative_path = parsed.path[len(urlsplit(REPO_RAW_PREFIX).path):]
        local_path = REPO_ROOT / relative_path
        assert local_path.is_file(), f"{url} points at {local_path} which is missing"


def check_url(url, attempts=4, as_browser=False):
    """Asserts that a url is usable, retrying transient failures.

    Files that are stored in this repository are checked on disk rather than
    over HTTP. A file added by a pull request is not on main until that branch
    is merged, so fetching it would fail for exactly the change that adds it.
    Looking for the file on disk tests the same thing, that the url in the
    registry corresponds to a real file.

    Only UNTESTED_URL is skipped because of its Cloudflare challenge. Every
    other URL is fetched with a bounded, streamed GET; HTTP failures, including
    other Cloudflare challenges, fail. Each URL is a separate test so a blocked
    host cannot prevent the other libraries from being checked.
    """
    if url == UNTESTED_URL:
        pytest.skip(f"{url}: Cloudflare challenge blocks the automated check; this URL is not tested")

    if url.startswith(REPO_RAW_PREFIX):
        validate_url(url)
        return

    status_code = None
    error = None
    for attempt in range(attempts):
        if attempt:
            time.sleep(2**attempt)
        headers = {'User-Agent': 'Mozilla/5.0'} if as_browser else {}
        try:
            with requests.get(url, stream=True, headers=headers, timeout=(10, 30)) as response:
                status_code = response.status_code
                if status_code in (200, 206):
                    return
                error = f"HTTP {status_code}"
        except requests.RequestException as exc:
            error = str(exc)
    pytest.fail(f"{url} returned {error} on {attempts} attempts")


def convert_urls():
    for library, releases in all_release_details.items():
        for release, particles in releases.items():
            for particle, file_types in particles.items():
                for file_type, value in file_types.items():
                    for file in value['compressed_files']:
                        url = value['base_url'] + file + value.get('url_suffix', '')
                        yield pytest.param(url, value.get('as_browser', False),
                                           id=f"{library}-{release}-{particle}-{file_type}-{file}")


@pytest.mark.network
@pytest.mark.parametrize('url,as_browser', list(convert_urls()))
def test_convert_urls(url, as_browser):
    check_url(url, as_browser=as_browser)


def h5_urls():
    for library, releases in all_h5_release_details.items():
        for release, particles in releases.items():
            for particle, value in particles.items():
                for file in value['compressed_files']:
                    url = value['base_url'] + file
                    yield pytest.param(url, id=f"{library}-{release}-{particle}-{file}")


@pytest.mark.network
@pytest.mark.parametrize('url', list(h5_urls()))
def test_h5_urls(url):
    check_url(url)


def xml_urls():
    for library, releases in all_chain_release_details.items():
        for release, branching_ratios in releases.items():
            for branching_ratio in branching_ratios:
                url = all_chain_release_details[library][release][branching_ratio]['chain']['url']
                yield pytest.param(url, id=f"{library}-{release}-{branching_ratio}")


@pytest.mark.network
@pytest.mark.parametrize('url', list(xml_urls()))
def test_xml_urls(url):
    check_url(url)


def decay_urls():
    for library, releases in all_decay_release_details.items():
        for release, particles in releases.items():
            for particle, value in particles.items():
                base_urls = value['base_url']
                if isinstance(base_urls, str):
                    base_urls = [base_urls]
                for base_url in base_urls:
                    for file in value['compressed_files']:
                        yield pytest.param(base_url + file,
                                           id=f"{library}-{release}-{particle}-{file}")


@pytest.mark.network
@pytest.mark.parametrize('url', list(decay_urls()))
def test_decay_urls(url):
    check_url(url)


# Validate every registry entry offline, including the URL not tested over HTTP.
@pytest.mark.parametrize('url,as_browser', list(convert_urls()))
def test_convert_url_registry(url, as_browser):
    validate_url(url)


@pytest.mark.parametrize('url', list(h5_urls()) + list(xml_urls()) + list(decay_urls()))
def test_url_registry(url):
    validate_url(url)


# Offline regressions for the URL checker stay unmarked.
@pytest.fixture
def http_response(monkeypatch):
    response = MagicMock(status_code=200, headers={})
    response.__enter__.return_value = response
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, 'get', get)
    monkeypatch.setattr(time, 'sleep', lambda _: None)
    return get, response


@pytest.mark.parametrize('url', [
    'http://example.org/data.zip',
    'https://example.org/data.zip?download=1',
    UNTESTED_URL,
])
def test_valid_url_syntax_does_not_request_http(http_response, url):
    get, _ = http_response
    validate_url(url)
    get.assert_not_called()


@pytest.mark.parametrize('url', [
    '',
    'data.zip',
    'ftp://example.org/data.zip',
    'https:///data.zip',
    'https://',
    'https://example.org',
    'https://example.org/',
    'https://example.org/data/',
    ' https://example.org/data.zip',
    'https://exam ple.org/data.zip',
    'https://example.org/data\t.zip',
    'https://example.org/data.zip\n',
])
def test_malformed_registry_url_fails(url):
    with pytest.raises(AssertionError):
        validate_url(url)


@pytest.mark.parametrize('checker', [validate_url, check_url])
@pytest.mark.parametrize('suffix', ['', '?download=1'])
def test_repository_file_is_checked_locally(monkeypatch, tmp_path, http_response, checker, suffix):
    get, _ = http_response
    monkeypatch.setitem(globals(), 'REPO_ROOT', tmp_path)
    (tmp_path / 'chain.xml').write_text('<chain/>')
    checker(REPO_RAW_PREFIX + 'chain.xml' + suffix)
    get.assert_not_called()


@pytest.mark.parametrize('checker', [validate_url, check_url])
def test_missing_repository_file_fails(monkeypatch, tmp_path, http_response, checker):
    get, _ = http_response
    monkeypatch.setitem(globals(), 'REPO_ROOT', tmp_path)
    with pytest.raises(AssertionError, match='missing.xml.*missing'):
        checker(REPO_RAW_PREFIX + 'missing.xml')
    get.assert_not_called()


@pytest.mark.parametrize('status', [200, 206])
def test_success_closes_response(http_response, status):
    get, response = http_response
    response.status_code = status
    check_url('https://example.org/data', as_browser=True)
    get.assert_called_once_with('https://example.org/data', stream=True,
                                headers={'User-Agent': 'Mozilla/5.0'}, timeout=(10, 30))
    response.__exit__.assert_called_once()


def test_only_exact_fendl_url_is_not_tested(http_response):
    get, _ = http_response
    with pytest.raises(pytest.skip.Exception, match='Cloudflare challenge.*not tested'):
        check_url('https://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-endf.zip')
    get.assert_not_called()


@pytest.mark.parametrize('url', [
    'https://example.org/data',
    'https://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2b-neutron-endf.zip',
    'https://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-ace.zip',
    'https://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-endf.zip?download=1',
    'https://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-endf.zip/',
    'https://www-nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-endf.zip',
    'http://nds.iaea.org/fendl/data/neutron/fendl-FENDL-3.2c-neutron-endf.zip',
    'https://nds.iaea.org/public/download-endf/TENDL-2019/n/n-C013.zip',
])
def test_other_cloudflare_challenges_fail(http_response, url):
    get, response = http_response
    response.status_code = 403
    response.headers = {'cf-mitigated': 'challenge'}
    with pytest.raises(pytest.fail.Exception, match='HTTP 403'):
        check_url(url, attempts=2)
    assert get.call_count == 2
    assert response.__exit__.call_count == 2


@pytest.mark.parametrize('status', [403, 404, 429, 500])
def test_ordinary_http_errors_fail(http_response, status):
    get, response = http_response
    response.status_code = status
    with pytest.raises(pytest.fail.Exception, match=f'HTTP {status}'):
        check_url('https://example.org/data', attempts=2)
    assert get.call_count == 2
    assert response.__exit__.call_count == 2


def test_network_errors_fail(http_response):
    get, _ = http_response
    get.side_effect = requests.Timeout('timed out')
    with pytest.raises(pytest.fail.Exception, match='timed out'):
        check_url('https://example.org/data', attempts=2)
    assert get.call_count == 2


def test_transient_failure_is_retried(http_response):
    get, response = http_response
    get.side_effect = [requests.Timeout('timed out'), response]
    check_url('https://example.org/data')
    assert get.call_count == 2
