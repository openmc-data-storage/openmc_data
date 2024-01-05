import argparse
from pathlib import Path
import openmc.deplete


parser = argparse.ArgumentParser(
    prog="reduce_chain",
    description="Removes nuclides with short half lives from OpenMC chain files",
)
parser.add_argument(
    "-i", "--chain_in", type=Path, required=True, help="Path of the input chain file"
)
parser.add_argument(
    "-o",
    "--chain_out",
    type=Path,
    required=True,
    help="Path of the produced chain file",
)

parser.add_argument(
    "-hl",
    "--half_life",
    type=float,
    required=True,
    default=1e15,
    help=(
        "Value of half life in seconds to use when filtering out nuclides, "
        "half lives below the specified half life nuclides will be excluded "
        "from the output chain file"
    )
        
)

args = parser.parse_args()


def remove_long_half_life_nuclides(chain_in: Path, chain_out: Path, half_life: float):
    chain_full = openmc.deplete.Chain.from_xml(chain_in)
    stable = [
        nuc.name
        for nuc in chain_full.nuclides
        if nuc.half_life is None or nuc.half_life > half_life
    ]

    chain_reduced = chain_full.reduce(stable)
    chain_reduced.export_to_xml(chain_out)


def main():
    remove_long_half_life_nuclides(args.chain_in, args.chain_out, args.half_life)


if __name__ == "__main__":
    main()
