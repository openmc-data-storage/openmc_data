#!/usr/bin/env python3

"""
Downloads preprocessed a chain file in xml format for use with OpenMc depletion
simulations.
"""

import argparse
from pathlib import Path
from urllib.parse import urljoin

from openmc_data.urls_xml import all_chain_release_details
from openmc_data.utils import download


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(description=__doc__, formatter_class=CustomFormatter)
parser.add_argument(
    "-d",
    "--destination",
    type=Path,
    default=None,
    help="Directory to create new library in",
)
parser.add_argument(
    "-f",
    "--filename",
    type=Path,
    default=None,
    help="Filename for the xml chain file",
)
parser.add_argument(
    "-r",
    "--release",
    choices=["b7.1", "b8.0", "b8.1", "2017", "2019", "2025"],
    default="2019",
    help="The nuclear data library release version. The currently supported "
         "options are b7.1, b8.0 and b8.1 for endf and 2017, 2019 and 2025 for "
         "tendl.",
)
parser.add_argument(
    "-l",
    "--library",
    choices=["endf", "tendl"],
    default="tendl",
    help="The nuclear data library. The currently supported options are endf and tendl",
)
parser.add_argument(
    "-b",
    "--branching_ratios",
    choices=["None", "SFR", "PWR", "FNS", "FNS-ORIGEN"],
    default="FNS",
    help="The branching ratios applied to the chain file. None, SFR (sodium "
         "fast reactor) and PWR (pressurized water reactor) are available for "
         "every library and release. FNS (fusion neutron source) is available "
         "for the tendl releases, with branching ratios for the production of "
         "metastable states collapsed from the TENDL isomeric production data "
         "with a fusion spectrum. FNS-ORIGEN is an earlier tendl 2017 and 2019 "
         "chain whose branching ratios come from ORIGEN rather than from TENDL. "
         "The tendl chains use decay data and neutron induced fission yields "
         "from ENDF/B-VIII.0. There is an option to use JEFF 3.3 if you "
         "generate your own chain file with the generate_tendl_chain command "
         "line tool.",
)

parser.set_defaults()
args = parser.parse_args()


def main():

    releases = all_chain_release_details[args.library]
    if args.release not in releases:
        raise ValueError(
            f"release {args.release} is not available for the {args.library} "
            f"library, options are {sorted(releases.keys())}"
        )
    branching_ratios = releases[args.release]
    if args.branching_ratios not in branching_ratios:
        raise ValueError(
            f"branching_ratios {args.branching_ratios} is not available for "
            f"{args.library} {args.release}, options are "
            f"{sorted(branching_ratios.keys())}"
        )

    details = branching_ratios[args.branching_ratios]["chain"]

    if args.filename is None:
        # the branching ratios are included in the filename so that chain files
        # with different branching ratios don't overwrite each other
        name_parts = ["chain", args.library, args.release]
        if args.branching_ratios != "None":
            name_parts.append(args.branching_ratios.lower())
        args.filename = Path("-".join(name_parts) + ".xml")
        print(f'Using default filename {args.filename}')

    download(
        details["url"],
        output_path=args.destination,
        output_filename=args.filename,
    )


if __name__ == "__main__":
    main()
