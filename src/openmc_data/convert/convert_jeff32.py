"""Compatibility alias for JEFF-3.2 (including its original HDF5 default)."""

from openmc_data.convert.convert_jeff import _main


def main(argv=None):
    return _main(argv, default_release="3.2", allowed_releases=("3.2",), default_libver="latest")


if __name__ == "__main__":
    main()
