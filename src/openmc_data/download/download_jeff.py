#!/usr/bin/env python3

"""
Downloads official JEFF HDF5 libraries and cross_sections.xml from openmc.org
for use with OpenMC. Includes JEFF neutron and thermal scattering data, plus
ENDF/B photoatomic and atomic relaxation data (VIII.0 for JEFF 3.3, VIII.1 for 4.0).
"""

import argparse
from pathlib import Path
from urllib.parse import urljoin

from openmc_data.urls_h5 import all_h5_release_details
from openmc_data.utils import download, extract


def main(argv=None):
    """Download and optionally extract an official JEFF HDF5 library."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-d", "--destination", type=Path, default=Path(),
        help="Parent directory for jeff-<release>-download and jeff-<release>-hdf5",
    )
    parser.add_argument("-r", "--release", choices=["3.3", "4.0"], default="4.0",
                        help="JEFF release")
    for flag, default, help_text in (
        ("download", True, "Download files listed on openmc.org"),
        ("extract", True, "Extract archive files"),
        ("cleanup", False, "Remove archives after successful extraction"),
    ):
        parser.add_argument("--" + flag, action="store_true", default=default, help=help_text)
        parser.add_argument("--no-" + flag, dest=flag, action="store_false")
    args = parser.parse_args(argv)

    details = all_h5_release_details["jeff"][args.release]["neutron-photon"]
    download_path = args.destination / f"jeff-{args.release}-download"
    destination = args.destination / f"jeff-{args.release}-hdf5"

    if args.download:
        # Archive and extracted sizes are not recorded, so do not estimate them.
        for filename in details["compressed_files"]:
            download(urljoin(details["base_url"], filename), output_path=download_path)

    if args.extract:
        extract(
            compressed_files=[download_path / f for f in details["compressed_files"]],
            extraction_dir=destination,
            del_compressed_file=args.cleanup,
        )


if __name__ == "__main__":
    main()