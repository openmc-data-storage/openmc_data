import hashlib
import shutil
import tarfile
import threading
import time
from typing import Iterable
import warnings
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .urls import all_release_details

try:
    import openmc.data
except ModuleNotFoundError:
    openmc = None

_BLOCK_SIZE = 16384


def format_duration(seconds):
    """Format a number of seconds as a ``H:MM:SS`` string."""
    if seconds is None or seconds != seconds:  # None or NaN
        return '--:--:--'
    seconds = int(round(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f'{hours:d}:{minutes:02d}:{secs:02d}'


class ProgressTracker:
    """Track progress through a fixed number of items and estimate the time
    remaining.

    The estimate is a simple extrapolation from the average time taken per
    completed item so far. Use :meth:`starting` for serial loops (call it just
    before processing each item) and :meth:`callback` with a
    ``multiprocessing.Pool`` (pass the returned function as the ``apply_async``
    callback so progress is reported as each item completes).

    Parameters
    ----------
    total : int
        Total number of items that will be processed.
    verb : str
        Word printed at the start of each progress line, e.g. ``'Converting'``.
    """

    def __init__(self, total, verb='Converting'):
        self.total = max(int(total), 0)
        self.verb = verb
        self.count = 0
        self.start = time.monotonic()
        self._lock = threading.Lock()

    def _format(self, position, completed, name):
        elapsed = time.monotonic() - self.start
        eta = elapsed / completed * (self.total - completed) if completed > 0 else None
        pct = 100 * position / self.total if self.total else 100
        line = (f'{self.verb} [{position}/{self.total} {pct:3.0f}%] '
                f'elapsed {format_duration(elapsed)} ETA {format_duration(eta)}')
        return f'{line}: {name}' if name else line

    def starting(self, name=''):
        """Print a progress line for an item that is about to be processed.

        The ETA is based on the items completed before this one, which is the
        appropriate estimate for a serial loop.
        """
        with self._lock:
            self.count += 1
            line = self._format(self.count, self.count - 1, name)
        print(line, flush=True)

    def complete(self, name=''):
        """Advance the counter and print a progress line for a finished item."""
        with self._lock:
            self.count += 1
            line = self._format(self.count, self.count, name)
        print(line, flush=True)

    def callback(self, name=''):
        """Return a one-argument function suitable as an ``apply_async``
        ``callback`` / ``error_callback`` that reports completion of ``name``."""
        def _callback(_result=None):
            self.complete(name)
        return _callback


def _require_openmc():
    if openmc is None:
        raise ModuleNotFoundError(
            "openmc is required for neutron and thermal data processing. "
            "Install openmc before calling this function."
        )

def state_download_size(compressed_file_size, uncompressed_file_size, units):
    """Prints a standard message to users displaying the amount of storage
    space required to run the script"""

    msg = (f"WARNING: This script will download up to {compressed_file_size} {units} "
           "of data. Extracting and processing the data may require as much "
           f"as {uncompressed_file_size} {units} of additional free disk space.")
    warnings.warn(msg)


def get_file_types(particles, script_type='convert'):
    if script_type == 'convert':

        ft = {}
        for particle in particles:
            ft[particle] = {'photon':'endf', 'neutron':'ace'}[particle]
    return ft

def calculate_download_size(library_name, release, particles, file_type,units='GB'):
    """Prints a standard message to users displaying the amount of storage
    space required to run the script"""

    release_details = all_release_details[library_name][release]

    compressed_file_size = 0
    uncompressed_file_size = 0
    for p in particles:
        compressed_file_size += release_details[p][file_type[p]]["compressed_file_size"]
        uncompressed_file_size += release_details[p][file_type[p]]["uncompressed_file_size"]
    state_download_size(compressed_file_size, uncompressed_file_size, units)
 

def process_neutron(path, output_dir, libver, temperatures=None):
    """Process ENDF neutron sublibrary file into HDF5 and write into a
    specified output directory."""
    _require_openmc()
    print(f'Converting: {path}')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            data = openmc.data.IncidentNeutron.from_njoy(
                path, temperatures=temperatures
            )
    except Exception as e:
        print(path, e)
        raise
    h5_file = output_dir / f'{data.name}.h5'
    print(f'Writing {h5_file} ...')
    data.export_to_hdf5(h5_file, 'w', libver=libver)


def process_thermal(path_neutron, path_thermal, output_dir, libver):
    """Process ENDF thermal scattering sublibrary file into HDF5 and write into a
    specified output directory."""
    _require_openmc()
    print(f'Converting: {path_thermal}')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            data = openmc.data.ThermalScattering.from_njoy(
                path_neutron, path_thermal
            )
    except Exception as e:
        print(path_neutron, path_thermal, e)
        raise
    h5_file = output_dir / f'{data.name}.h5'
    print(f'Writing {h5_file} ...')
    data.export_to_hdf5(h5_file, 'w', libver=libver)


def extract(
    compressed_files,
    extraction_dir,
    del_compressed_file=False,
    verbose=True,
):
    """Extracts zip, tar.gz or tgz compressed files

    Parameters
    ----------
    compressed_files : [os.PathLike, str iterable]
        The file or and iterables of files to extract.
    extraction_dir : str
        The directory to extract the files to.
    del_compressed_file : bool
        Whether the compressed file should be deleted (True) or not (False)
    verbose : bool
        Controls the printing to terminal, if True filenames of the extracted
        files will be printed.
    """
    Path.mkdir(extraction_dir, parents=True, exist_ok=True)

    print(f'Extracting {compressed_files} to {extraction_dir}')
    if isinstance(compressed_files, (str, Path)) or not isinstance(compressed_files, Iterable):
        compressed_files = [compressed_files]

    for f in compressed_files:
        if str(f).endswith('.zip'):
            with zipfile.ZipFile(f, 'r') as zipf:
                if verbose:
                    print(f'Extracting {f} to {extraction_dir}')
                zipf.extractall(path=extraction_dir)

        elif str(f).endswith('.tar.gz') or str(f).endswith('.tgz') or str(f).endswith('.tar.bz2') or str(f).endswith('.tar.xz')  or str(f).endswith('.xz'):
            with tarfile.open(f, 'r') as tgz:
                if verbose:
                    print(f'Extracting {f} to {extraction_dir}')
                tgz.extractall(path=extraction_dir)
        elif str(f).endswith('.asc'):
            shutil.copy(f, extraction_dir)
        else:
            raise ValueError('File type not currently supported by extraction '
                             f'function {str(f)}')

    if del_compressed_file:
        for compressed_file in compressed_files:
            Path(compressed_file).unlink(missing_ok=True)


def apply_updates(update_archives, target_dir, pattern='*.dat'):
    """Overwrite evaluations in an extracted library with updated versions

    Each archive is extracted on its own and its files replace the files of
    the same name in ``target_dir``. Archives are applied in the order given,
    so a later update to an evaluation takes precedence over an earlier one.
    Files that are not in ``target_dir``, such as corrections to another
    sublibrary, are skipped, but an archive none of whose files are in
    ``target_dir`` is an error.

    Parameters
    ----------
    update_archives : iterable of os.PathLike or str
        Compressed update archives, oldest first.
    target_dir : os.PathLike or str
        The directory that holds the extracted evaluations to update.
    pattern : str
        Glob pattern matching the evaluation files within each archive.
    """
    target_dir = Path(target_dir)
    for archive in update_archives:
        with TemporaryDirectory(prefix='.update-', dir=target_dir.parent) as tmp:
            extract(archive, Path(tmp), verbose=False)
            updated_files = sorted(Path(tmp).rglob(pattern))
            if not updated_files:
                raise FileNotFoundError(f'No {pattern} files found in {archive}')
            # An update can also correct other sublibraries, such as the
            # JENDL-5 _u20, _0K, _300K and _act files, which are skipped
            applied = [f for f in updated_files if (target_dir / f.name).is_file()]
            skipped = [f.name for f in updated_files if f not in applied]
            if not applied:
                raise FileNotFoundError(
                    f'None of the files in {archive} are in {target_dir}: '
                    f'{", ".join(skipped)}')
            for updated_file in applied:
                shutil.copyfile(updated_file, target_dir / updated_file.name)
            message = f'Applied {len(applied)} updated files from {archive}'
            if skipped:
                message += (f', skipped {len(skipped)} that are not in '
                            f'{target_dir.name}: {", ".join(skipped)}')
            print(message)


def _file_md5(path):
    """Hash large archives without loading them into memory."""
    checksum = hashlib.md5()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(_BLOCK_SIZE), b''):
            checksum.update(chunk)
    return checksum.hexdigest()


def download(
    url: str,
    checksum=None,
    as_browser: bool=False,
    output_path=None,
    output_filename=None,
    **kwargs
):
    """Download file from a URL

    Parameters
    ----------
    url : str
        URL from which to download
    checksum : str or None
        MD5 checksum to check against
    as_browser : bool
        Change User-Agent header to appear as a browser
    output_path : str or Path
        Specifies the directory location to save the downloaded file
    output_filename : str or Path
        Specifies the filename save the downloaded file. If left as None the
        filename of the download file is obtained from the url filename
    kwargs : dict
        Keyword arguments passed to :func:`urllib.request.urlopen`

    Returns
    -------
    local_path : pathlib.Path
        Name of file written locally

    """

    if output_filename is None:
        output_filename = Path(Path(urlparse(url).path).name)
        print(f'Using default output_filename {output_filename}')

    if output_path is None:
        local_path = Path(output_filename)
    else:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        local_path = Path(output_path) / output_filename

    # A file that matches its checksum needs no network access at all, which
    # also lets a file saved by hand stand in for a server that refuses scripts
    if checksum is not None and local_path.is_file() and _file_md5(local_path) == checksum:
        print(f'Skipping {local_path}, already downloaded')
        return local_path

    if as_browser:
        page = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    else:
        page = url

    try:
        response = urlopen(page, **kwargs)
    except (URLError, OSError) as error:
        return _manual_download(url, local_path, checksum, error)

    with response:
        # Bot protection often answers with a 200 status and an HTML page
        # instead of the file, which would otherwise be saved as the archive
        content_type = response.headers.get_content_type()
        if content_type == 'text/html' and not urlparse(url).path.endswith(('.html', '.htm')):
            return _manual_download(
                url, local_path, checksum,
                'the server sent a web page instead of the file')

        # Get file size from header
        file_size = response.length

        # Check if file already downloaded
        if file_size is not None and local_path.is_file():
            if (local_path.stat().st_size == file_size
                    and (checksum is None or _file_md5(local_path) == checksum)):
                print(f'Skipping {local_path}, already downloaded')
                return local_path

        # Copy file to disk in chunks
        print(f'Downloading URL {url} to {local_path}')
        downloaded = 0
        with open(local_path, 'wb') as fh:
            while True:
                chunk = response.read(_BLOCK_SIZE)
                if not chunk:
                    break
                fh.write(chunk)
                downloaded += len(chunk)
                if file_size:
                    status = '{:10}  [{:3.2f}%]'.format(
                        downloaded, downloaded * 100. / file_size)
                else:
                    status = f'{downloaded:10} bytes'
                print(status + '\b'*len(status), end='', flush=True)
            print('')

    if file_size is not None and downloaded != file_size:
        raise OSError(f"Incomplete download of {url}: expected {file_size} bytes, received {downloaded}")

    if checksum is not None:
        downloadsum = _file_md5(local_path)
        if downloadsum != checksum:
            raise OSError(_manual_download_message(
                url, local_path, checksum,
                f'the MD5 checksum of the downloaded file is {downloadsum}'))

    return local_path


def _manual_download_message(url, local_path, checksum, reason):
    message = (
        f'Could not download {url} ({reason}).\n'
        f'Download it in a web browser and save it as\n'
        f'    {Path(local_path).resolve()}\n'
        f'then run the same command again.'
    )
    if checksum is not None:
        message += f' The file is expected to have the MD5 checksum {checksum}.'
    return message


def _manual_download(url, local_path, checksum, reason):
    """Use a file saved by hand when the server refuses, or explain how to."""
    local_path = Path(local_path)
    if local_path.is_file() and checksum is None:
        warnings.warn(f'Could not download {url} ({reason}), using the existing '
                      f'file {local_path}, which could not be verified')
        return local_path
    raise OSError(_manual_download_message(url, local_path, checksum, reason))
