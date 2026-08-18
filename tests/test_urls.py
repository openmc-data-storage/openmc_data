
import time
from pathlib import Path

import requests

from openmc_data import all_release_details, all_h5_release_details, all_chain_release_details


# urls that serve a file kept in this repository, see check_url
REPO_RAW_PREFIX = "https://github.com/openmc-data-storage/openmc_data/raw/main/"
REPO_ROOT = Path(__file__).resolve().parent.parent


def check_url(url, attempts=4):
    """Asserts that a url is usable, retrying transient failures.

    Files that are stored in this repository are checked on disk rather than
    over HTTP. A file added by a pull request is not on main until that branch
    is merged, so fetching it would fail for exactly the change that adds it.
    Looking for the file on disk tests the same thing, that the url in the
    registry corresponds to a real file.

    Every other url is fetched. GitHub and some of the data hosts answer 429 or
    an occasional 404 when this suite requests hundreds of files in one job, so
    a failure is retried with a growing wait before it is treated as real.
    """
    if url.startswith(REPO_RAW_PREFIX):
        local_path = REPO_ROOT / url[len(REPO_RAW_PREFIX):]
        assert local_path.is_file(), f"{url} points at {local_path} which is missing"
        return

    status_code = None
    for attempt in range(attempts):
        if attempt:
            time.sleep(2**attempt)
        status_code = requests.get(url, stream=True).status_code
        if status_code == 200:
            return
    assert status_code == 200, (
        f"{url} returned {status_code} on {attempts} attempts"
    )


def test_convert_urls():
    """Cycles through all the urls in each nuclear data library and checks
    that they return a status 200 code (success)"""

    for library, releases in all_release_details.items():
        for release, particles in releases.items():
            for particle, file_types in particles.items():
                for file_types, value in file_types.items():
                    for file in value['compressed_files']:
                        url = value['base_url'] + file
                        # printing output so that in the event of a failure the
                        # failing url can be identified
                        print(library, release, particle, url)
                        check_url(url)


def test_h5_urls():
    """Cycles through all the h5 urls in each nuclear data library and checks
    that they return a status 200 code (success)"""

    for library, releases in all_h5_release_details.items():
        for release, particles in releases.items():
            for particle, value in particles.items():
                for file in value['compressed_files']:
                    url = value['base_url'] + file
                    print(library, release, particle, url)
                    check_url(url)


def test_xml_urls():
    """Cycles through all the xml urls in each nuclear data library and checks
    that they return a status 200 code (success)"""

    for library, releases in all_chain_release_details.items():
        for release, branching_ratios in releases.items():
            for branching_ratio in branching_ratios:
                url = all_chain_release_details[library][release][branching_ratio]['chain']['url']
                print(library, release, branching_ratio, url)
                check_url(url)
