import hashlib
import io
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
    calls = []
    def urlopen(request, **kwargs):
        calls.append((request, kwargs))
        return response
    monkeypatch.setattr(utils, 'urlopen', urlopen)
    path = utils.download('https://example.invalid/library.zip/content', as_browser=True,
                          output_path=tmp_path, output_filename='library.zip', timeout=10)
    assert path == target
    assert calls[0][0].get_header('User-agent') == 'Mozilla/5.0'
    assert calls[0][1] == {'timeout': 10}
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


@pytest.mark.parametrize('length', [None, 0])
def test_empty_download(tmp_path, monkeypatch, length):
    monkeypatch.setattr(utils, 'urlopen', lambda *a, **k: Response(b'', length))
    path = utils.download('https://example.invalid/empty', output_path=tmp_path)
    assert path.read_bytes() == b''


def test_wrong_cached_size_redownloaded(tmp_path, monkeypatch):
    (tmp_path / 'file').write_bytes(b'partial')
    monkeypatch.setattr(utils, 'urlopen', lambda *a, **k: Response(b'new', 3))
    assert utils.download('https://example.invalid/file', output_path=tmp_path).read_bytes() == b'new'


@pytest.mark.parametrize('valid', [False, True])
def test_unknown_length_checksum(tmp_path, monkeypatch, valid):
    monkeypatch.setattr(utils, 'urlopen', lambda *a, **k: Response(b'payload', None))
    checksum = hashlib.md5(b'payload' if valid else b'wrong').hexdigest()
    if valid:
        assert utils.download('https://example.invalid/file', checksum=checksum, output_path=tmp_path).is_file()
    else:
        with pytest.raises(OSError, match='MD5 checksum'):
            utils.download('https://example.invalid/file', checksum=checksum, output_path=tmp_path)


@pytest.mark.parametrize('valid_cache', [False, True])
def test_known_length_cached_checksum(tmp_path, monkeypatch, valid_cache):
    payload = b'payload'
    target = tmp_path / 'file'
    target.write_bytes(payload if valid_cache else b'invalid')
    response = Response(payload, len(payload))
    monkeypatch.setattr(utils, 'urlopen', lambda *a, **k: response)
    checksum = hashlib.md5(payload).hexdigest()
    assert utils.download('https://example.invalid/file', checksum=checksum,
                          output_path=tmp_path).read_bytes() == payload
    assert bool(response.read_sizes) is not valid_cache
    assert response.closed


def test_checksum_uses_bounded_reads(tmp_path, monkeypatch):
    from pathlib import Path

    payload = b'x' * (2*utils._BLOCK_SIZE + 17)
    response = Response(payload, None)
    monkeypatch.setattr(utils, 'urlopen', lambda *a, **k: response)
    opened = Path.open
    reads = []

    def bounded(path, mode='r', *args, **kwargs):
        if mode == 'rb':
            stream = Response(payload, len(payload))
            reads.append(stream)
            return stream
        return opened(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', bounded)
    utils.download('https://example.invalid/file', checksum=hashlib.md5(payload).hexdigest(),
                   output_path=tmp_path)
    assert len(reads) == 1
    assert len(reads[0].read_sizes) == 4
    assert reads[0].closed


def test_truncated_download_fails(tmp_path, monkeypatch):
    response = Response(b'partial', 100)
    monkeypatch.setattr(utils, 'urlopen', lambda *a, **k: response)
    with pytest.raises(OSError, match='Incomplete download'):
        utils.download('https://example.invalid/file', output_path=tmp_path)
    assert response.closed
