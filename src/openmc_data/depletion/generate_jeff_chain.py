#!/usr/bin/env python3

import argparse
from pathlib import Path
from urllib.parse import urljoin

import openmc.deplete

from openmc_data.utils import download, extract
from openmc_data import all_decay_release_details


# Parse command line arguments
parser = argparse.ArgumentParser(prog="generate_jeff_chain",
    description="Generates a OpenMC chain file from JEFF nuclear data files",
)
parser.add_argument('-r', '--release', choices=['3.3'],
                    default='3.3', help="The nuclear data library release "
                    "version. The currently supported options are 3.3")
parser.add_argument(
    "-d",
    "--destination",
    type=Path,
    default=None,
    help="filename of the chain file xml file produced. If left as None then "
    "the filename will follow this format 'chain_jeff_{release}.xml'",
)
args = parser.parse_args()


def main():

    library_name = 'jeff'

    cwd = Path.cwd()

    endf_files_dir = cwd.joinpath('-'.join([library_name, args.release, 'endf']))
    download_path = cwd.joinpath('-'.join([library_name, args.release, 'download']))

    neutron_dir = endf_files_dir / "neutrons"
    decay_dir = endf_files_dir / "decay"
    nfy_dir = endf_files_dir / "nfy"

    # This dictionary contains all the unique information about each release.
    # This can be extended to accommodated new releases

    for file_type, extract_dir in zip(['neutron', 'decay', 'nfy'], [neutron_dir, decay_dir, nfy_dir]):
        details = all_decay_release_details[library_name][args.release][file_type]
        for base_url, file in zip(details['base_url'], details['compressed_files']):
            downloaded_file = download(
                url=urljoin(base_url, file),
                output_path=download_path
            )

        extract(downloaded_file, extract_dir)

    neutron_files = list(neutron_dir.rglob("*.jeff33"))
    decay_files = list(decay_dir.rglob("*.ASC"))

    nfy_file = download_path / all_decay_release_details[library_name][args.release]["nfy"]["compressed_files"][0]
    assert nfy_file.suffix == ".asc"
    fixed_nfy_file = nfy_file.parent / (nfy_file.stem + "-fixed.asc")

    with open(nfy_file, "r") as original:
        with open(fixed_nfy_file, "w") as fixed:
            fixed.write(" " * 70 + " 1  0    0\n")
            fixed.write(original.read())

    fpy_files = [fixed_nfy_file]

    # check files exist
    for flist, ftype in [(decay_files, "decay"), (neutron_files, "neutron"),
                         (fpy_files, "neutron fission product yield")]:
        if not flist:
            raise IOError(f"No {ftype} endf files found in {endf_files_dir}")

    chain = openmc.deplete.Chain.from_endf(
        decay_files=decay_files,
        fpy_files=fpy_files,
        neutron_files=neutron_files,
        reactions=list(openmc.deplete.chain.REACTIONS.keys())
    )

    if args.destination is None:
        args.destination = f'chain_{library_name}_{args.release}.xml'

    chain.export_to_xml(args.destination)
    print(f'Chain file written to {args.destination}')


if __name__ == '__main__':
    main()
