#!/usr/bin/env python3
"""Legacy JEFF 3.3 entry point; implementation lives in generate_jeff."""

from .generate_jeff import _main


def main(argv=None):
    _main(argv, legacy=True)


if __name__ == '__main__':
    main()
