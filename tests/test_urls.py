
import requests

from openmc_data import all_release_details, all_h5_release_details, all_chain_release_details


def test_convert_urls():
    """Cycles through all the urls in each nuclear data library and checks
    that they return a status 200 code (success)"""

    print("library, release, particle, response.status_code")
    for library, releases in all_release_details.items():
        for release, particles in releases.items():
            for particle, file_types in particles.items():
                for file_types, value in file_types.items():
                    for file in value['compressed_files']:
                        url = value['base_url'] + file
                        print(library, release, particle, url)
                        response = requests.get(url, stream=True)
                        print(library, release, particle, url, response.status_code)
                        # printing output so that in the event of a failure the
                        # failing url can be identified
                        assert response.status_code == 200


def test_h5_urls():
    """Cycles through all the h5 urls in each nuclear data library and checks
    that they return a status 200 code (success)"""

    print("library, release, particle, response.status_code")
    for library, releases in all_h5_release_details.items():
        for release, particles in releases.items():
            for particle, value in particles.items():
                for file in value['compressed_files']:
                    url = value['base_url'] + file
                    print(library, release, particle, url)
                    response = requests.get(url, stream=True)
                    print(library, release, particle, url, response.status_code)
                    # printing output so that in the event of a failure the
                    # failing url can be identified
                    assert response.status_code == 200


def test_xml_urls():
    """Cycles through all the xml urls in each nuclear data library and checks
    that they return a status 200 code (success)"""

    print("library, release, particle, response.status_code")
    for library, releases in all_chain_release_details.items():
        for release, branching_ratios in releases.items():
            for branching_ratio in branching_ratios:
                url = all_chain_release_details[library][release][branching_ratio]['chain']['url']
                print(library, release, branching_ratio, url)
                response = requests.get(url, stream=True)
                print(library, release, url, branching_ratio, response.status_code)
                # printing output so that in the event of a failure the
                # failing url can be identified
                assert response.status_code == 200
