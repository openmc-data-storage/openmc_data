#!/usr/bin/env python3

"""
Generates a JSON file of branching ratios for the production of metastable
states, collapsed with a user provided multigroup neutron flux.

The branching ratios are taken from the isomeric production data in the ENDF
neutron files. The MF=8 section of each evaluation identifies the isomeric
states of every reaction product, their excitation energies, and whether the
production data is stored as multiplicities in MF=9 or as cross sections in
MF=10. The one group branching ratio for each isomeric state is the reaction
rate weighted average

    branching ratio = sum(production * flux) / sum(all productions * flux)

which is the weighting that preserves the production rate of each isomer when
the chain file only has a single energy group.

Branching ratios are spectrum dependent so a flux that is representative of the
simulation is needed. Fusion neutron source spectra can be found in the IAEA
CoNDERC FNS benchmark (https://nds.iaea.org/conderc/fusion/) as FISPACT-II
fluxes files, which can be passed in with the --fispact-fluxes option.

The resulting JSON file can be applied to a chain file with the
add_branching_ratios command line tool.
"""

import argparse
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    prog="generate_branching_ratios", description=__doc__, formatter_class=CustomFormatter
)
parser.add_argument(
    "-n",
    "--neutron-dir",
    type=Path,
    required=True,
    help="Directory of ENDF neutron files, searched recursively. This is the "
    "neutron directory that generate_tendl_chain creates when it downloads and "
    "extracts the ENDF files",
)
parser.add_argument(
    "--pattern",
    default="*.tendl",
    help="Glob pattern used to find the ENDF neutron files in the neutron directory",
)
flux_group = parser.add_mutually_exclusive_group(required=True)
flux_group.add_argument(
    "--fispact-fluxes",
    type=Path,
    help="A FISPACT-II fluxes file, read with pypact so that the group "
    "boundaries and the ordering of the flux values are both taken from the "
    "file format. This is the recommended option as it avoids having to "
    "specify --energy-bins and --flux-order",
)
flux_group.add_argument(
    "--flux",
    type=Path,
    help="File of whitespace separated multigroup flux values, one per group. "
    "Requires --energy-bins",
)
parser.add_argument(
    "--energy-bins",
    default="CCFE-709",
    help="Group boundaries in eV for --flux, either the name of an OpenMC group "
    "structure (for example CCFE-709 or VITAMIN-J-175) or a file of whitespace "
    "separated boundaries in ascending order",
)
parser.add_argument(
    "--flux-order",
    choices=["ascending", "descending"],
    default="descending",
    help="Whether the values in --flux run from low to high energy or from high "
    "to low energy. FISPACT-II fluxes files are stored descending",
)
parser.add_argument(
    "--cross-sections",
    type=Path,
    default=None,
    help="Path to a cross_sections.xml file. Reaction cross sections needed to "
    "weight the MF=9 multiplicities are read from this HDF5 library instead of "
    "being reconstructed with NJOY, which is much quicker if the library "
    "already exists. The library should be made from the same ENDF files",
)
parser.add_argument(
    "--temperature",
    type=float,
    default=294.0,
    help="Temperature in Kelvin used when reconstructing cross sections",
)
parser.add_argument(
    "--chain",
    type=Path,
    default=None,
    help="Optional chain file used to check that the parent and target nuclides "
    "exist in the chain. Branching ratios for nuclides that are not in the "
    "chain are dropped and reported",
)
parser.add_argument(
    "-o",
    "--output",
    type=Path,
    default=Path("branching_ratios.json"),
    help="Filename of the JSON file produced",
)

parser.set_defaults()
args = parser.parse_args()


def read_flux():
    """Return (group boundaries, flux values) both in ascending energy order."""
    if args.fispact_fluxes is not None:
        import pypact as pp

        fluxes_file = pp.FluxesFile()
        pp.from_file(fluxes_file, str(args.fispact_fluxes))
        # pypact reverses the values so that they match its ascending boundaries
        boundaries = np.asarray(fluxes_file.boundaries, dtype=float)
        values = np.asarray(fluxes_file.values, dtype=float)
    else:
        import openmc.mgxs

        values = np.array(args.flux.read_text().replace(",", " ").split(), dtype=float)
        if args.energy_bins in openmc.mgxs.GROUP_STRUCTURES:
            boundaries = np.asarray(
                openmc.mgxs.GROUP_STRUCTURES[args.energy_bins], dtype=float
            )
        else:
            boundaries = np.array(
                Path(args.energy_bins).read_text().replace(",", " ").split(), dtype=float
            )
        if args.flux_order == "descending":
            values = values[::-1]

    if len(boundaries) != len(values) + 1:
        raise ValueError(
            f"Got {len(values)} flux values which needs {len(values) + 1} group "
            f"boundaries but {len(boundaries)} boundaries were found"
        )
    return boundaries, values


def isomer_targets(evaluation, mt):
    """Map the ENDF final state number to a nuclide name for one MF=8 section.

    The final state number (LFS) counts excited states of the product while
    OpenMC nuclide names count metastable states, and the two are not the same.
    TENDL only tabulates the ground state and the states that are metastable, so
    the metastable index is found by ranking the states of each product by their
    excitation energy (ELFS).

    Returns {LFS: (nuclide name, LMF)} where LMF is the file, 9 or 10, that
    holds the production data.
    """
    from openmc.data import gnds_name
    from openmc.data.endf import get_cont_record, get_head_record, get_list_record

    section = io.StringIO(evaluation.section[(8, mt)])
    *_, number_states, no_data = get_head_record(section)

    states = []
    for _ in range(number_states):
        if no_data == 1:
            items = get_cont_record(section)
        else:
            items, _values = get_list_record(section)
        za_product, excitation, lmf, lfs = items[:4]
        states.append((int(za_product), float(excitation), int(lmf), int(lfs)))

    # the final state numbers index into the MF=9 or MF=10 subsections so they
    # have to be unique for the mapping to be unambiguous
    final_states = [state[3] for state in states]
    if len(set(final_states)) != len(final_states):
        return {}

    targets = {}
    for za_product in {state[0] for state in states}:
        product_states = sorted(
            (state for state in states if state[0] == za_product), key=lambda s: s[1]
        )
        metastable = 0
        for _za, excitation, lmf, lfs in product_states:
            if excitation > 0.0:
                metastable += 1
            z, a = divmod(za_product, 1000)
            targets[lfs] = (gnds_name(z, a, metastable), lmf)
    return targets


def production_data(evaluation, mf, mt):
    """Return {LFS: Tabulated1D} from an MF=9 or MF=10 section."""
    from openmc.data.endf import get_head_record, get_tab1_record

    section = io.StringIO(evaluation.section[(mf, mt)])
    *_, number_states, _ = get_head_record(section)
    data = {}
    for _ in range(number_states):
        params, tabulated = get_tab1_record(section)
        data[params[3]] = tabulated
    return data


class CrossSections:
    """Reaction cross sections used to weight MF=9 multiplicities."""

    def __init__(self):
        self._library = None
        # reconstructing a nuclide is by far the slowest part of this script so
        # the most recent one is kept, the reactions of a nuclide are processed
        # together so only one needs to be held at a time
        self._cache_key = None
        self._cache = None
        if args.cross_sections is not None:
            import openmc.data

            self._library = openmc.data.DataLibrary.from_xml(args.cross_sections)

    def _nuclide(self, path, name):
        import openmc.data

        if self._cache_key == path:
            return self._cache
        if self._library is not None:
            entry = self._library.get_by_material(name, data_type="neutron")
            nuclide = None
            if entry is not None:
                try:
                    nuclide = openmc.data.IncidentNeutron.from_hdf5(entry["path"])
                except OSError:
                    # the paths in a cross_sections.xml are relative to it, which
                    # does not resolve if the file is reached through a symlink
                    nuclide = None
        else:
            # NJOY reconstructs the resonances, which cannot be skipped as the
            # MF=3 cross section is only the background in the resolved range
            try:
                nuclide = openmc.data.IncidentNeutron.from_njoy(
                    str(path), temperatures=[args.temperature]
                )
            except Exception:
                nuclide = None
        self._cache_key = path
        self._cache = nuclide
        return nuclide

    def get(self, path, name, mt, energies):
        """Return the cross section for one reaction at the given energies."""
        nuclide = self._nuclide(path, name)
        if nuclide is None or mt not in nuclide:
            return None
        cross_section = nuclide[mt].xs
        key = f"{int(args.temperature)}K"
        if key not in cross_section:
            key = sorted(cross_section)[0]
        return cross_section[key](energies)


def chain_nuclides():
    """Return the set of nuclide names in the chain file, or None."""
    if args.chain is None:
        return None
    import openmc.deplete

    return {nuclide.name for nuclide in openmc.deplete.Chain.from_xml(args.chain).nuclides}


def main():

    import openmc.deplete.chain
    from openmc.data.endf import Evaluation

    mt_to_reaction = {
        mt: name
        for name, info in openmc.deplete.chain.REACTIONS.items()
        for mt in info.mts
    }

    boundaries, flux = read_flux()
    midpoints = 0.5 * (boundaries[:-1] + boundaries[1:])
    print(
        f"Read {len(flux)} flux groups spanning {boundaries[0]:.3e} to "
        f"{boundaries[-1]:.3e} eV"
    )

    paths = sorted(args.neutron_dir.rglob(args.pattern))
    if not paths:
        raise ValueError(
            f"No files matching {args.pattern} found in {args.neutron_dir}"
        )
    print(f"Found {len(paths)} ENDF neutron files in {args.neutron_dir}")

    in_chain = chain_nuclides()
    cross_sections = CrossSections()

    branching_ratios = defaultdict(dict)
    skipped = Counter()
    skipped_detail = defaultdict(list)

    for path in paths:
        try:
            evaluation = Evaluation(path)
        except Exception as e:
            skipped["unreadable evaluation"] += 1
            skipped_detail["unreadable evaluation"].append(f"{path.name} ({e})")
            continue
        parent = evaluation.gnds_name

        for mf, mt in sorted(evaluation.section):
            if mf != 8 or mt not in mt_to_reaction:
                continue
            reaction = mt_to_reaction[mt]
            targets = isomer_targets(evaluation, mt)

            # only reactions that make more than one state of a product branch
            if len({name for name, _lmf in targets.values()}) < 2:
                continue

            lmf = {lmf for _name, lmf in targets.values()}
            if len(lmf) != 1 or lmf.pop() not in (9, 10):
                skipped["unsupported MF=8 layout"] += 1
                skipped_detail["unsupported MF=8 layout"].append(f"{parent} {reaction}")
                continue
            data_mf = next(iter(targets.values()))[1]
            if (data_mf, mt) not in evaluation.section:
                skipped[f"MF={data_mf} section missing"] += 1
                skipped_detail[f"MF={data_mf} section missing"].append(
                    f"{parent} {reaction}"
                )
                continue

            production = production_data(evaluation, data_mf, mt)
            weight = flux
            if data_mf == 9:
                # MF=9 holds multiplicities so the reaction cross section is
                # needed to turn them into a reaction rate weighting
                cross_section = cross_sections.get(path, parent, mt, midpoints)
                if cross_section is None:
                    skipped["no cross section for MF=9 weighting"] += 1
                    skipped_detail["no cross section for MF=9 weighting"].append(
                        f"{parent} {reaction}"
                    )
                    continue
                weight = cross_section * flux

            rates = {
                lfs: float(np.sum(tabulated(midpoints) * weight))
                for lfs, tabulated in production.items()
                if lfs in targets
            }
            total = sum(rates.values())
            if total <= 0.0:
                skipped["zero reaction rate for this flux"] += 1
                skipped_detail["zero reaction rate for this flux"].append(
                    f"{parent} {reaction}"
                )
                continue

            ratios = {}
            for lfs, rate in rates.items():
                ratios[targets[lfs][0]] = rate / total

            if in_chain is not None:
                missing = {parent} | set(ratios)
                missing -= in_chain
                if missing:
                    skipped["not in chain file"] += 1
                    skipped_detail["not in chain file"].append(
                        f"{parent} {reaction} ({', '.join(sorted(missing))})"
                    )
                    continue

            branching_ratios[reaction][parent] = ratios

    total_channels = sum(len(parents) for parents in branching_ratios.values())
    print(f"\nWrote branching ratios for {total_channels} reactions")
    for reaction in sorted(branching_ratios):
        print(f"  {reaction:12s} {len(branching_ratios[reaction]):5d} nuclides")

    if skipped:
        print("\nSkipped channels")
        for reason, count in skipped.most_common():
            examples = ", ".join(skipped_detail[reason][:4])
            more = "" if count <= 4 else f", and {count - 4} more"
            print(f"  {count:5d}  {reason}: {examples}{more}")

    ordered = {
        reaction: dict(sorted(branching_ratios[reaction].items()))
        for reaction in sorted(branching_ratios)
    }
    args.output.write_text(json.dumps(ordered, indent=4) + "\n")
    print(f"\nwritten {args.output}")


if __name__ == "__main__":
    main()
