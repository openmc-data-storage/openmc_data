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


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def main(argv=None):
    """Download and optionally extract an official JEFF HDF5 library."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=CustomFormatter)
    parser.add_argument(
        "-d",
        "--destination",
        type=Path,
        default=None,
        help="Parent directory for jeff-<release>-download and jeff-<release>-hdf5",
    )
    parser.add_argument(
        "--download", action="store_true", help="Download files listed on openmc.org"
    )
    parser.add_argument(
        "--no-download",
        dest="download",
        action="store_false",
        help="Use previously downloaded files",
    )
    parser.add_argument("--extract", action="store_true", help="Extract archive files")
    parser.add_argument(
        "--no-extract",
        dest="extract",
        action="store_false",
        help="Do not extract archive files",
    )
    parser.add_argument(
        "-r",
        "--release",
        choices=["3.3", "4.0"],
        default="4.0",
        help="The JEFF nuclear data library release version",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove downloaded archives after successful extraction",
    )
    parser.add_argument(
        "--no-cleanup",
        dest="cleanup",
        action="store_false",
        help="Keep downloaded archives after extraction",
    )
    parser.set_defaults(download=True, extract=True, cleanup=False)
    args = parser.parse_args(argv)

    details = all_h5_release_details["jeff"][args.release]["neutron-photon"]
    root = args.destination if args.destination is not None else Path()
    download_path = root / f"jeff-{args.release}-download"
    destination = root / f"jeff-{args.release}-hdf5"

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