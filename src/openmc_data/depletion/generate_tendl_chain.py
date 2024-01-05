#!/usr/bin/env python3

"""
Generate a depletion chain based on TENDL 2019 data. Note that TENDL 2019 does
not contain any decay or fission product yield (FPY) sublibraries, so these must
be borrowed from another library. The --lib flag for this script indicates what
library should be used for decay and FPY evaluations and defaults to JEFF 3.3.
"""

import argparse
from pathlib import Path
from urllib.parse import urljoin

import openmc.data
import openmc.deplete as dep

from openmc_data.utils import download, extract
from openmc_data import all_decay_release_details

# Parse command line arguments
parser = argparse.ArgumentParser(prog="generate_tendl_chain",
    description="Generates a OpenMC chain file from TENDL nuclear data files",
)
parser.add_argument(
    "--lib",
    choices=("jeff33", "endf80"),
    default="jeff33",
    help="Library to use for decay and fission product yields",
)
parser.add_argument(
    "-r",
    "--release",
    choices=["2015", "2017", "2019", "2021"],
    default="2021",
    help="The nuclear data library release "
    "version. The currently supported options are 2019, "
    "and 2021.",
)
parser.add_argument(
    "-d",
    "--destination",
    type=Path,
    default=None,
    help="filename of the chain file xml file produced. If left as None then "
    "the filename will follow this format 'chain_tendl_{release}_{lib}.xml'",
)
parser.add_argument("--extract", action="store_true", help="Extract tar/zip files")
parser.add_argument(
    "--no-extract",
    dest="extract",
    action="store_false",
    help="Do not extract tar/zip files",
)
parser.set_defaults(extract=True)
args = parser.parse_args()


def fix_jeff33_nfy(path):
    print(f"Fixing TPID in {path.name}...")
    new_path = path.with_name(path.name + "_fixed")
    if not new_path.exists():
        with path.open("r") as f:
            data = f.read()
        with new_path.open("w") as f:
            # Write missing TPID line
            f.write(" " * 66 + "   1 0  0    0\n")
            f.write(data)
    return new_path


def main():

    library_name = "tendl"

    cwd = Path.cwd()

    endf_files_dir = cwd.joinpath("-".join([library_name, args.release, "endf"]))
    download_path = cwd.joinpath("-".join([library_name, args.release, "download"]))

    neutron_dir = endf_files_dir / "neutron"
    decay_dir = endf_files_dir / "decay"
    nfy_dir = endf_files_dir / "nfy"

    # This dictionary contains all the unique information about each release.
    # This can be extended to accommodated new releases
    release_details = all_decay_release_details["tendl"][args.release]

    # adds in either jeff or endf neutron fission yields and decay data
    if args.lib == "jeff33":
        release_details["decay"] = all_decay_release_details['jeff']['3.3']["decay"]
        release_details["nfy"] = all_decay_release_details['jeff']['3.3']["nfy"]
    elif args.lib == "endf80":
        release_details["decay"] = all_decay_release_details['endf']['b8.0']["decay"]
        release_details["nfy"] = all_decay_release_details['endf']['b8.0']["nfy"]
    else:
        raise ValueError(
            f"lib argument must be either jeff33 or endf80 and can not be {args.lib}"
        )

    # ==========================================================================
    # Incident neutron data
    for f in release_details["neutron"]["compressed_files"]:
        downloaded_file = download(
            url=urljoin(release_details["neutron"]["base_url"], f),
            output_path=download_path,
        )

        extract(downloaded_file, neutron_dir)

    neutron_files = [
        p
        for p in list(neutron_dir.rglob("*.tendl"))
    ]
    print(neutron_files)
    # ==========================================================================
    # Decay and fission product yield data
    print(release_details)
    decay_zip = download(
        urljoin(
            release_details["decay"]["base_url"][0],
            release_details["decay"]["compressed_files"][0],
        ),
        output_path=decay_dir,
    )
    nfy_zip = download(
        urljoin(
            release_details["nfy"]["base_url"][0],
            release_details["nfy"]["compressed_files"][0],
        ),
        output_path=nfy_dir,
    )

    extract(decay_zip, decay_dir)

    if args.lib == "jeff33":
        nfy_file = nfy_zip  # file is already uncompressed
        decay_files = list(decay_dir.glob("*.ASC"))
        nfy_file_fixed = fix_jeff33_nfy(nfy_file)
        nfy_files = openmc.data.endf.get_evaluations(nfy_file_fixed)

    elif args.lib == "endf80":
        decay_files = list(decay_dir.rglob("*.endf"))
        extract(nfy_zip, nfy_dir)
        nfy_files = list(nfy_dir.rglob("*.endf"))

    chain = dep.Chain.from_endf(
        decay_files, nfy_files, neutron_files, reactions=dep.chain.REACTIONS.keys()
    )

    if args.destination is None:
        args.destination = f"chain_{library_name}_{args.release}_{args.lib}.xml"

    chain.export_to_xml(args.destination)
    print(f"Chain file written to {args.destination}")


if __name__ == "__main__":
    main()
