import hashlib
import io
from pathlib import Path
import tarfile
from unittest.mock import Mock

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


class Response(io.BytesIO):
    def __init__(self, payload, length):
        super().__init__(payload)
        self.length = length
        self.read_sizes = []

    def read(self, size=-1):
        assert size == utils._BLOCK_SIZE, 'Download must use bounded reads'
        self.read_sizes.append(size)
        return super().read(size)


@pytest.mark.parametrize('known_length', [False, True])
@pytest.mark.parametrize('existing', [False, True])
def test_download_streaming_length_and_cache(tmp_path, monkeypatch, capsys, known_length, existing):
    payload = b'x' * (2*utils._BLOCK_SIZE + 17)
    response = Response(payload, len(payload) if known_length else None)
    target = tmp_path / 'library.zip'
    if existing:
        target.write_bytes(b'o' * len(payload))
    urlopen = Mock(return_value=response)
    monkeypatch.setattr(utils, 'urlopen', urlopen)
    path = utils.download('https://example.invalid/library.zip/content', as_browser=True,
                          output_path=tmp_path, output_filename='library.zip', timeout=10)
    assert path == target
    assert urlopen.call_args.args[0].get_header('User-agent') == 'Mozilla/5.0'
    assert urlopen.call_args.kwargs == {'timeout': 10}
    if existing and known_length:
        assert target.read_bytes() == b'o' * len(payload)
        assert not response.read_sizes
    else:
        assert target.read_bytes() == payload
        assert len(response.read_sizes) == 4
    output = capsys.readouterr().out
    if not known_length:
        assert 'bytes' in output and '%' not in output and 'Skipping' not in output
    assert response.closed


@pytest.mark.parametrize('payload,length,cached,checksum_data,error', [
    (b'', None, None, None, None), (b'', 0, None, None, None),
    (b'new', 3, b'partial', None, None),
    (b'payload', None, None, b'payload', None),
    (b'payload', None, None, b'wrong', 'MD5 checksum'),
    (b'payload', 7, b'payload', b'payload', None),
    (b'payload', 7, b'invalid', b'payload', None),
    (b'partial', 100, None, None, 'Incomplete download'),
])
def test_download_validation(tmp_path, monkeypatch, payload, length, cached, checksum_data, error):
    target = tmp_path / 'file'
    if cached is not None:
        target.write_bytes(cached)
    response = Response(payload, length)
    monkeypatch.setattr(utils, 'urlopen', Mock(return_value=response))
    checksum = hashlib.md5(checksum_data).hexdigest() if checksum_data is not None else None
    if error:
        with pytest.raises(OSError, match=error):
            utils.download('https://example.invalid/file', checksum=checksum, output_path=tmp_path)
    else:
        assert utils.download('https://example.invalid/file', checksum=checksum,
                              output_path=tmp_path).read_bytes() == payload
        assert bool(response.read_sizes) is not (cached == payload)
    assert response.closed


def test_checksum_uses_bounded_reads(tmp_path, monkeypatch):
    payload = b'x' * (2*utils._BLOCK_SIZE + 17)
    stream = Response(payload, len(payload))
    opened = Mock(return_value=stream)
    monkeypatch.setattr(Path, 'open', opened)
    assert utils._file_md5(tmp_path / 'file') == hashlib.md5(payload).hexdigest()
    opened.assert_called_once_with('rb')
    assert len(stream.read_sizes) == 4
    assert stream.closed
