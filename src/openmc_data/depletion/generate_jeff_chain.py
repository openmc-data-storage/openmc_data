#!/usr/bin/env python3

"""Generate an OpenMC depletion chain from JEFF ENDF evaluations.

JEFF distributes its radioactive decay and fission product yield
sub-libraries as single ENDF tapes holding every material. The tapes are
split into their individual materials before the chain is built, as OpenMC
only reads the first material of a file.
"""

import argparse
from pathlib import Path
import shutil

import openmc.data
import openmc.deplete

from openmc_data.utils import download, extract
from openmc_data import all_decay_release_details


LIBRARY_NAME = 'jeff'
RELEASES = tuple(all_decay_release_details[LIBRARY_NAME])
ARCHIVE_SUFFIXES = ('.zip', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz', '.xz')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="generate_jeff_chain",
        description="Generates a OpenMC chain file from JEFF nuclear data files",
    )
    parser.add_argument('-r', '--release', choices=RELEASES, default='4.0',
                        help="The nuclear data library release version. The "
                        f"currently supported options are {', '.join(RELEASES)}")
    parser.add_argument(
        "-d",
        "--destination",
        type=Path,
        default=None,
        help="filename of the chain file xml file produced. If left as None then "
        "the filename will follow this format 'chain_jeff_{release}.xml'",
    )
    return parser.parse_args(argv)


def fetch(details, download_path, extract_dir):
    """Download one sub-library and return the paths of its ENDF files."""
    paths = []
    for base_url, name, checksum in zip(details['base_url'],
                                        details['compressed_files'],
                                        details['checksums']):
        downloaded_file = download(
            url=base_url + name + details.get('url_suffix', ''),
            checksum=checksum,
            as_browser=details.get('as_browser', False),
            output_path=download_path,
            output_filename=name,
        )
        if name.endswith(ARCHIVE_SUFFIXES):
            extract(downloaded_file, extract_dir)
        else:
            paths.append(downloaded_file)
    if 'endf_files' in details:
        paths.extend(sorted(extract_dir.rglob(details['endf_files'])))
    return paths


def with_tape_id(path):
    """Return a copy of an ENDF tape with a TPID record added if it lacks one.

    The JEFF fission product yield tapes start directly with the first
    material, which ENDF readers misread as the tape identifier.
    """
    with open(path) as fh:
        first_line = fh.readline()
    if first_line[70:75] == ' 0  0':
        return path
    fixed = path.with_name(f'{path.stem}-fixed{path.suffix}')
    with open(path) as original, open(fixed, 'w') as out:
        out.write(" " * 66 + "   1 0  0    0\n")
        shutil.copyfileobj(original, out)
    return fixed


def materials(paths):
    """Split ENDF tapes into a list of their individual materials."""
    return [material for path in paths
            for material in openmc.data.endf.get_evaluations(with_tape_id(path))]


def main(argv=None):
    args = parse_args(argv)

    cwd = Path.cwd()
    endf_files_dir = cwd / f'{LIBRARY_NAME}-{args.release}-endf'
    download_path = cwd / f'{LIBRARY_NAME}-{args.release}-download'
    release_details = all_decay_release_details[LIBRARY_NAME][args.release]

    files = {}
    for file_type, extract_dir in [('neutron', 'neutrons'), ('decay', 'decay'),
                                   ('nfy', 'nfy')]:
        files[file_type] = fetch(release_details[file_type], download_path,
                                 endf_files_dir / extract_dir)

    # check files exist
    for file_type, description in [('decay', 'decay'), ('neutron', 'neutron'),
                                   ('nfy', 'neutron fission product yield')]:
        if not files[file_type]:
            raise IOError(f"No {description} endf files found in {endf_files_dir}")

    chain = openmc.deplete.Chain.from_endf(
        decay_files=materials(files['decay']),
        fpy_files=materials(files['nfy']),
        neutron_files=files['neutron'],
        reactions=list(openmc.deplete.chain.REACTIONS.keys())
    )

    if args.destination is None:
        args.destination = f'chain_{LIBRARY_NAME}_{args.release}.xml'

    chain.export_to_xml(args.destination)
    print(f'Chain file written to {args.destination}')


if __name__ == '__main__':
    main()
