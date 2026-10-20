#!/usr/bin/env python3
"""Convert OECD/NEA JEFF neutron and thermal ACE data to OpenMC HDF5.

Temperature selections apply to neutron archives. Thermal tables use their own
temperature grids and are all retained. JEFF-4.0 supplies only the public
selected TSL subset (12 cases, 316 tables), not the complete TSL evaluation set.
"""

import argparse
from collections import defaultdict
from dataclasses import dataclass
import math
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory
import warnings

from openmc_data import ProgressTracker, all_release_details, download, extract


RELEASES = ("3.2", "3.3", "4.0")


@dataclass(frozen=True)
class TableSource:
    """A lightweight index entry, never an in-memory ACE data array."""

    path: Path
    table_name: str
    temperature: float
    name: str
    zaid: int = None


def _header(path):
    """Read only the ASCII ACE header, including the newer 2.x header form."""
    import openmc.data

    try:
        with path.open(encoding="ascii") as stream:
            words = stream.readline(1024).split()
            if re.fullmatch(r"\d\.\d\.\d", words[0]):
                name = words[1]
                temperature = float(stream.readline(1024).split()[1])
            else:
                name = words[0]
                temperature = float(words[2])
        temperature *= 1.e6 / openmc.data.K_BOLTZMANN
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("invalid temperature")
        if not re.fullmatch(r"[^.\s]+\.\d+[ct]", name):
            raise ValueError("invalid table name")
    except (ValueError, IndexError, UnicodeError) as exc:
        raise ValueError(f"Invalid or empty ACE header: {path}") from exc
    return name, temperature


def _neutron_groups(root, release, temperatures):
    import openmc.data

    groups = defaultdict(dict)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if release == "3.2":
            match = re.fullmatch(r"([A-Z][a-z]?)(\d+)([mM]?)\.ACE", path.name)
            if not match:
                continue  # Ignore .dir files and redundant *-293.ACE TSL tables.
            symbol, mass, state = match.groups()
            z = openmc.data.ATOMIC_NUMBER[symbol]
            directory = re.fullmatch(r"ACEs_(\d+)K", path.parent.name)
            if directory:
                selected = directory[1]
            elif path.parent == root:
                selected = "293"  # New 293 K archive has no enclosing directory.
            else:
                continue
            filename_temperature = float(selected)
        else:
            suffix = r"\.ace" if release == "3.3" else ""
            match = re.fullmatch(
                r"(\d+)-([A-Z][a-z]?)-(\d+)([gm])-(\d+(?:\.\d+)?)" + suffix,
                path.name,
            )
            if not match:
                continue
            z, symbol, mass, state, temp = match.groups()
            z = int(z)
            filename_temperature = float(temp)
            # Do not use Path.stem: 293.6 and 0.1 are not file extensions.
            selected = "293" if release == "4.0" and temp == "293.6" else f"{float(temp):g}"
            if selected in temperatures and release == "3.3" and path.parent.name != f"ace_{selected}":
                raise ValueError(f"Inconsistent neutron temperature directory: {path}")
        if selected not in temperatures:
            continue
        if openmc.data.ATOMIC_SYMBOL[z] != symbol:
            raise ValueError(f"Inconsistent neutron identity: {path}")
        mass = int(mass)
        metastable = int(state.lower() == "m")
        name = openmc.data.gnds_name(z, mass, metastable)
        table_name, temperature = _header(path)
        if not table_name.endswith("c"):
            raise ValueError(f"Not a neutron ACE table: {path}")
        zaid = int(table_name.split(".")[0])
        metadata = openmc.data.ace.get_metadata(zaid)
        if metadata[2:4] != (z, mass):
            raise ValueError(f"ACE header and filename identify different nuclides: {path}")
        if not math.isclose(temperature, filename_temperature, abs_tol=1.0):
            raise ValueError(f"ACE header and filename identify different temperatures: {path}")
        if selected in groups[name]:
            raise ValueError(f"Duplicate neutron table for {name} at {selected} K: {path}")
        # Normalize every temperature in memory, including already-corrected caches
        # and the MCNP Am242 exception. Never rewrite a downloaded ACE file.
        corrected_zaid = 1000*z + mass + 400*metastable
        groups[name][selected] = TableSource(path, table_name, temperature, name, corrected_zaid)

    if not groups:
        raise FileNotFoundError(f"No requested JEFF-{release} neutron ACE tables in {root}")
    for name, entries in groups.items():
        missing = set(temperatures) - entries.keys()
        if missing:
            raise FileNotFoundError(f"Missing neutron tables for {name} at {sorted(missing, key=float)} K")
    return {name: list(entries.values()) for name, entries in groups.items()}


def _thermal_name(identity):
    import openmc.data

    # OpenMC can fuzzy-match unknown names to *different* materials. Preserve an
    # unknown identity instead, and make the unsupported alias visible to users.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        name = openmc.data.thermal.get_thermal_name(identity)
    if caught:
        name = f"c_{identity}"
        warnings.warn(f"Unrecognized thermal ACE identity {identity!r}; using {name!r} without fuzzy matching.")
    return name


def _thermal_groups(root, release, details):
    groups = defaultdict(list)
    paths = {p for pattern in details["ace_paths"] for p in root.glob(pattern) if p.is_file()}
    # Retain the old 3.3 material coverage check without using a previous
    # material's data when a glob is empty. Grouping itself uses ACE identity.
    missing = [group for group in details.get("required_file_groups", ())
               if not any(re.fullmatch(re.escape(group) + r".*-\d+\.ace", p.name) for p in paths)]
    if missing:
        raise FileNotFoundError(f"Missing JEFF-{release} thermal materials: {', '.join(missing)}")
    for path in sorted(paths):
        if release == "4.0" and not re.fullmatch(r"[^.]+\.\d+_\d+(?:\.\d+)?", path.name):
            continue  # Archive directory/index files are not ACE tables.
        table_name, temperature = _header(path)
        if not table_name.endswith("t"):
            raise ValueError(f"Not a thermal ACE table: {path}")
        identity = table_name.split(".")[0]
        if release == "3.2":
            identity = identity.rstrip("0123456789")  # lw10.32t -> lw
        groups[identity].append((path, table_name, temperature))
    if not groups:
        raise FileNotFoundError(f"No JEFF-{release} thermal ACE tables in {root}")
    for key, actual in (("selected_cases", len(groups)),
                        ("selected_tables", sum(map(len, groups.values())))):
        if key in details and actual != details[key]:
            raise ValueError(f"Incomplete JEFF-{release} thermal subset: {key} expected {details[key]}, found {actual}")
    result = {}
    for identity, entries in groups.items():
        name = _thermal_name(identity)
        if name in result:
            raise ValueError(f"Thermal output name collision: {identity} maps to {name}")
        result[name] = [TableSource(path, table, temp, name) for path, table, temp in entries]
    return result


def _validate_outputs(groups, destination):
    """Reject silent OpenMC temperature deduplication and unsafe output names."""
    for name, entries in groups.items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise ValueError(f"Unsafe output name: {name!r}")
        entries.sort(key=lambda entry: entry.temperature)
        labels = [round(entry.temperature) for entry in entries]
        if len(set(labels)) != len(labels):
            raise ValueError(f"Duplicate OpenMC temperature for {name}: {labels}")
    for name in [f"{name}.h5" for name in groups] + ["cross_sections.xml"]:
        path = destination / name
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"Refusing to overwrite existing output: {path}")


def _convert_group(entries, thermal):
    import openmc.data

    cls = openmc.data.ThermalScattering if thermal else openmc.data.IncidentNeutron
    data = None
    for entry in entries:
        # Supply the name so OpenMC reads only the indexed table, not a whole
        # multi-table ACE library. Only this material is accumulated in memory.
        table = openmc.data.ace.get_table(entry.path, name=entry.table_name)
        if entry.zaid is not None:
            table.name = f"{entry.zaid}.{table.name.split('.')[1]}"
        kwargs = {"name": entry.name} if thermal else {}
        if data is None:
            data = cls.from_ace(table, **kwargs)
        else:
            data.add_temperature_from_ace(table, **kwargs)
        if data.name != entry.name:
            raise ValueError(f"Converted name {data.name} does not match {entry.name}: {entry.path}")
        del table
    if len(data.temperatures) != len(entries):
        raise ValueError(f"Conversion lost temperatures for {data.name}")
    return data


def _parser(default_release, allowed_releases, default_libver):
    choices = '; '.join(
        f"{release}: {', '.join(all_release_details['jeff'][release]['neutron']['ace']['temperatures'])}"
        for release in allowed_releases
    )
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"Available neutron archive temperatures (K), by release: {choices}",
    )
    parser.add_argument("-r", "--release", choices=allowed_releases, default=default_release)
    parser.add_argument("-t", "--temperatures", nargs="+", help="Neutron archive temperatures in K; default: all available for the release")
    parser.add_argument("-d", "--destination", type=Path, help="Direct output directory; default: jeff-<release>-hdf5")
    parser.add_argument("--libver", choices=("earliest", "latest"), default=default_libver)
    for option, default, help_text in (
        ("download", True, "Download selected neutron archives and the thermal archive"),
        ("extract", True, "Extract the downloaded archives"),
        ("cleanup", False, "Remove ACE and download cache directories only after success"),
    ):
        parser.add_argument(f"--{option}", dest=option, action="store_true", help=help_text)
        parser.add_argument(f"--no-{option}", dest=option, action="store_false", help=f"Do not {help_text.lower()}")
        parser.set_defaults(**{option: default})
    return parser


def _main(argv=None, *, default_release="4.0", allowed_releases=RELEASES, default_libver="latest"):
    parser = _parser(default_release, allowed_releases, default_libver)
    args = parser.parse_args(argv)
    details = all_release_details["jeff"][args.release]
    neutron = details["neutron"]["ace"]
    thermal = details["thermal"]["ace"]
    temperatures = args.temperatures if args.temperatures is not None else neutron["temperatures"]
    invalid = set(temperatures) - set(neutron["temperatures"])
    if invalid:
        parser.error(f"JEFF-{args.release} does not provide temperatures {sorted(invalid)}; choose from {', '.join(neutron['temperatures'])}")
    temperatures = sorted(set(temperatures), key=float)
    root = Path.cwd() / f"jeff-{args.release}-ace"
    downloads = Path.cwd() / f"jeff-{args.release}-download"
    destination = (args.destination or Path(f"jeff-{args.release}-hdf5")).resolve()
    for cache in (root.resolve(), downloads.resolve()):
        if destination == cache or cache in destination.parents:
            parser.error("Destination must be outside the ACE and download cache directories")

    archives = [(neutron, filename, temp) for filename, temp in
                zip(neutron["compressed_files"], neutron["temperatures"]) if temp in temperatures]
    archives += [(thermal, filename, None) for filename in thermal["compressed_files"]]
    if args.release == "4.0":
        print("JEFF-4.0 thermal data: public SELECTED subset only (12 cases, 316 tables).")
    if args.download:
        warnings.warn("JEFF ACE archives require multiple GB of download and working space; thermal grids are downloaded in full.")
        for source, filename, _ in archives:
            download(source["base_url"] + filename + source.get("url_suffix", ""),
                     as_browser=source.get("as_browser", False), output_path=downloads,
                     output_filename=filename)
    if args.extract:
        for _, filename, temp in archives:
            target = root / "ACEs_293K" if args.release == "3.2" and temp == "293" else root
            extract(downloads / filename, target, del_compressed_file=False)

    neutron_groups = _neutron_groups(root, args.release, temperatures)
    thermal_groups = _thermal_groups(root, args.release, thermal)
    if neutron_groups.keys() & thermal_groups.keys():
        raise ValueError("Neutron and thermal output name collision")
    groups = {**neutron_groups, **thermal_groups}
    _validate_outputs(groups, destination)
    destination.mkdir(parents=True, exist_ok=True)

    import openmc.data

    # Stage everything, including the relative-path XML, before publishing any
    # outputs. Failed conversions leave caches intact and no success manifest.
    with TemporaryDirectory(prefix=".jeff-", dir=destination) as temporary:
        stage = Path(temporary)
        library = openmc.data.DataLibrary()
        tracker = ProgressTracker(len(groups))
        for name, entries in sorted(groups.items()):
            tracker.starting(name)
            data = _convert_group(entries, name in thermal_groups)
            output = stage / f"{name}.h5"
            data.export_to_hdf5(output, "w", libver=args.libver)
            del data
            library.register_file(output)
        library.export_to_xml(stage / "cross_sections.xml")
        for name in groups:
            (stage / f"{name}.h5").replace(destination / f"{name}.h5")
        (stage / "cross_sections.xml").replace(destination / "cross_sections.xml")
    if args.cleanup:
        for cache in (downloads, root):
            if cache.exists():
                shutil.rmtree(cache)


def main(argv=None):
    """Run the unified converter; importing this module never parses arguments."""
    return _main(argv)


if __name__ == "__main__":
    main()