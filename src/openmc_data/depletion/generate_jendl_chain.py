#!/usr/bin/env python3

import argparse
import ssl
from pathlib import Path
from urllib.parse import urljoin

import openmc.deplete

from openmc_data.utils import download, extract
from openmc_data import all_decay_release_details


# Parse command line arguments
parser = argparse.ArgumentParser(prog="generate_jeff_chain",
    description="Generates a OpenMC chain file from JENDL nuclear data files",
)
parser.add_argument('-r', '--release', choices=['5.0'],
                    default='5.0', help="The nuclear data library release "
                    "version. The only currently supported option is 5.0.")
parser.add_argument(
    "-d",
    "--destination",
    type=Path,
    default=None,
    help="filename of the chain file xml file produced. If left as None then "
    "the filename will follow this format 'chain_jendl_{release}.xml'",
)
parser.add_argument(
    "--neutron",
    type=Path,
    default=[],
    nargs="+",
    help="Path to neutron endf files, if not provided, neutron files will be downloaded.",
)
parser.add_argument(
    "--decay",
    type=Path,
    default=[],
    nargs="+",
    help="Path to decay data files, if not provided, decay files will be downloaded.",
)
parser.add_argument(
    "--fpy",
    type=Path,
    default=[],
    nargs="+",
    help="Path to neutron fission product yield files, if not provided, fission yield files will be downloaded.",
)
args = parser.parse_args()

def main():

    library_name = 'jendl'

    cwd = Path.cwd()

    # DOWNLOAD NEUTRON DATA
    endf_files_dir = cwd.joinpath('-'.join([library_name, args.release, 'endf']))
    download_path = cwd.joinpath('-'.join([library_name, args.release, 'download']))
    neutron_files = args.neutron
    if not neutron_files:
        details = all_decay_release_details[library_name][args.release]['neutron']

        for f in details['compressed_files']:
            # Establish connection to URL
            download(
                urljoin(details['base_url'], f),
                context=ssl._create_unverified_context(),
                output_path=download_path
            )
        extract(
            compressed_files=[download_path / f for f in details['compressed_files']],
            extraction_dir=endf_files_dir,
            del_compressed_file=False
        )
        for erratum in details["errata"]:
            files = Path('.').rglob(erratum)
            for p in files:
                p.rename((endf_files_dir / details["endf_files"]).parent / p.name)
        neutron_files = endf_files_dir.glob(details['endf_files'])

    decay_files = args.decay
    if not decay_files:
        details = all_decay_release_details[library_name][args.release]['decay']
        for base_url, file in zip(details['base_url'], details['compressed_files']):
            downloaded_file = download(
                url=urljoin(base_url, file),
                output_path=Path(".")
            )

            extract([downloaded_file], Path("."))
        decay_files = list(Path('.').rglob(details["decay_files"]))

    fpy_files = args.fpy
    if not fpy_files:
        details = all_decay_release_details[library_name][args.release]['nfy']
        for base_url, file in zip(details['base_url'], details['compressed_files']):
            downloaded_file = download(
                url=urljoin(base_url, file),
                output_path=Path(".")
            )

            extract([downloaded_file], Path("."))
        fpy_files = list(Path('.').rglob(details["nfy_files"]))

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