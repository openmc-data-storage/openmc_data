#!/usr/bin/env python3
"""Scan a directory of OpenMC HDF5 data files and remove any that are corrupt.

Useful after an interrupted ``generate_*`` / ``convert_*`` run (e.g. Ctrl-C).
Those scripts resume by skipping ENDF/ACE files whose output ``.h5`` already
exists, checking only for existence -- not integrity. A file left half-written
when the process was killed is therefore treated as "done" and silently kept in
the library. Running this first deletes any unreadable ``.h5`` files so that a
rerun regenerates them.

Examples
--------
    # Remove any truncated/corrupt files (fast, opens each with h5py)
    remove_corrupt_h5 tendl-2025-hdf5

    # Also fully load each file with openmc (slower, neutron data only)
    remove_corrupt_h5 tendl-2025-hdf5 --deep

    # Report without deleting
    remove_corrupt_h5 tendl-2025-hdf5 --dry-run
"""
import argparse
import glob
import os

import h5py

try:
    import openmc.data
except ModuleNotFoundError:
    openmc = None


def check_file(path, deep=False):
    """Return an error string if ``path`` is corrupt, otherwise ``None``.

    The default check opens the file with h5py, which catches the common
    failure mode of a truncated write. ``deep=True`` additionally loads the
    file with :class:`openmc.data.IncidentNeutron`.
    """
    try:
        with h5py.File(path, "r"):
            pass
    except Exception as e:  # noqa: BLE001 - report any read failure
        return str(e)
    if deep:
        if openmc is None:
            raise ModuleNotFoundError(
                "openmc is required for --deep validation but is not installed."
            )
        try:
            openmc.data.IncidentNeutron.from_hdf5(path)
        except Exception as e:  # noqa: BLE001 - report any load failure
            return str(e)
    return None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "directory", help="Directory containing the .h5 files to check"
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Also fully load each file with openmc (slower, neutron data only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report corrupt files without deleting them",
    )
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.directory, "*.h5")))
    print(f"Scanning {len(files)} .h5 files in {args.directory} ...")
    removed = 0
    for f in files:
        reason = check_file(f, deep=args.deep)
        if reason is not None:
            action = "would remove" if args.dry_run else "removing"
            print(f"{action} corrupt: {f} -> {reason}")
            if not args.dry_run:
                os.remove(f)
            removed += 1
    verb = "corrupt" if args.dry_run else "removed"
    print(f"Done, {removed} {verb} file(s); {len(files) - removed} intact")


if __name__ == "__main__":
    main()
