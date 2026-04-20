try:
    # this works for python 3.7 and lower
    from importlib.metadata import version, PackageNotFoundError
except (ModuleNotFoundError, ImportError):
    # this works for python 3.8 and higher
    from importlib_metadata import version, PackageNotFoundError
try:
    __version__ = version("openmc_data")
except PackageNotFoundError:
    try:
        from setuptools_scm import get_version
    except ModuleNotFoundError:
        __version__ = "develop"
    else:
        __version__ = get_version(root="..", relative_to=__file__)

__all__ = ["__version__"]

from .utils import (
    calculate_download_size,
    download,
    extract,
    get_file_types,
    process_neutron,
    process_thermal,
    state_download_size,
)
from .urls import all_release_details
from .urls_h5 import all_h5_release_details
from .urls_xml import all_chain_release_details
from .urls_chain import all_decay_release_details
