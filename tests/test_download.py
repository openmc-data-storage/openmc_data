"""Offline tests for utils.download: urlopen is replaced, nothing is fetched."""

from email.message import Message
import hashlib
import io
from urllib.error import HTTPError

import pytest

from openmc_data import utils

URL = "https://example.org/data/library.tar.gz"


class Response(io.BytesIO):
    def __init__(self, data, content_type="application/gzip"):
        super().__init__(data)
        self.length = len(data)
        self.headers = Message()
        self.headers["Content-Type"] = content_type


@pytest.fixture
def urlopen(monkeypatch):
    calls = []

    def install(result):
        def fake(page, **kwargs):
            calls.append(page)
            if isinstance(result, Exception):
                raise result
            return result
        monkeypatch.setattr(utils, "urlopen", fake)
        return calls
    return install


def md5(data):
    return hashlib.md5(data).hexdigest()


def test_downloads_file(tmp_path, urlopen):
    urlopen(Response(b"archive"))
    path = utils.download(URL, checksum=md5(b"archive"), output_path=tmp_path)
    assert path == tmp_path / "library.tar.gz"
    assert path.read_bytes() == b"archive"


def test_verified_local_file_needs_no_network(tmp_path, urlopen):
    calls = urlopen(HTTPError(URL, 403, "Forbidden", None, None))
    (tmp_path / "library.tar.gz").write_bytes(b"saved by hand")
    path = utils.download(URL, checksum=md5(b"saved by hand"), output_path=tmp_path)
    assert path.read_bytes() == b"saved by hand"
    assert calls == []


@pytest.mark.parametrize("failure", [
    HTTPError(URL, 403, "Forbidden", None, None),
    ConnectionResetError("connection reset"),
    Response(b"<html>Request unsuccessful</html>", "text/html"),
], ids=["http-error", "network-error", "html-page"])
def test_failure_explains_manual_download(tmp_path, urlopen, failure):
    urlopen(failure)
    with pytest.raises(OSError) as error:
        utils.download(URL, checksum=md5(b"archive"), output_path=tmp_path)
    message = str(error.value)
    assert URL in message
    assert str((tmp_path / "library.tar.gz").resolve()) in message
    assert "web browser" in message
    assert md5(b"archive") in message
    assert not (tmp_path / "library.tar.gz").exists()


def test_html_page_is_not_saved_as_archive(tmp_path, urlopen):
    urlopen(Response(b"<html>blocked</html>", "text/html"))
    with pytest.raises(OSError, match="web page instead of the file"):
        utils.download(URL, output_path=tmp_path)
    assert not (tmp_path / "library.tar.gz").exists()


def test_html_url_may_return_html(tmp_path, urlopen):
    urlopen(Response(b"<html>page</html>", "text/html"))
    path = utils.download("https://example.org/index.html", output_path=tmp_path)
    assert path.read_bytes() == b"<html>page</html>"


def test_unverifiable_local_file_is_used_with_warning(tmp_path, urlopen):
    urlopen(HTTPError(URL, 403, "Forbidden", None, None))
    (tmp_path / "library.tar.gz").write_bytes(b"saved by hand")
    with pytest.warns(UserWarning, match="could not be verified"):
        path = utils.download(URL, output_path=tmp_path)
    assert path.read_bytes() == b"saved by hand"


def test_wrong_local_file_is_not_used(tmp_path, urlopen):
    urlopen(HTTPError(URL, 403, "Forbidden", None, None))
    (tmp_path / "library.tar.gz").write_bytes(b"something else")
    with pytest.raises(OSError, match="web browser"):
        utils.download(URL, checksum=md5(b"archive"), output_path=tmp_path)


def test_checksum_mismatch_explains_manual_download(tmp_path, urlopen):
    urlopen(Response(b"corrupt"))
    with pytest.raises(OSError) as error:
        utils.download(URL, checksum=md5(b"archive"), output_path=tmp_path)
    assert f"checksum of the downloaded file is {md5(b'corrupt')}" in str(error.value)
    assert "web browser" in str(error.value)
