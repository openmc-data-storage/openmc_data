"""Compatibility alias for JEFF-3.3 (including its original HDF5 default)."""

from openmc_data.convert.convert_jeff import _main


def main(argv=None):
    return _main(argv, default_release="3.3", allowed_releases=("3.3",), default_libver="earliest")


if __name__ == "__main__":
    main()
