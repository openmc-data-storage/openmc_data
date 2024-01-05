import argparse
import json
from pathlib import Path

import openmc.deplete


parser = argparse.ArgumentParser(prog="add_branching_ratio",
    description="Adds branching ratios to n,gamma reactions in OpenMC chain files",
)
parser.add_argument(
    "-i", "--chain_in", type=Path, required=True, help="Path of the input chain file"
)
parser.add_argument(
    "-b",
    "--branching_ratios",
    type=str,
    required=True,
    help='Path of the input branching ratios JSON file or the type of reactor for the branching ratio "SFR" or "PWR"',
)
parser.add_argument(
    "-o",
    "--chain_out",
    type=Path,
    required=True,
    help="Path of the produced chain file",
)
args = parser.parse_args()


def update_chain(chain_in, branching_ratios, chain_out):
    # Load existing chain
    chain = openmc.deplete.Chain.from_xml(chain_in)

    if branching_ratios.lower() == "sfr":
        branching_ratios = Path(__file__).parent / "branching_ratios_sfr.json"
    elif branching_ratios.lower() == "pwr":
        branching_ratios = Path(__file__).parent / "branching_ratios_pwr.json"

    # Set branching ratios
    with open(branching_ratios) as fh:
        all_branch_ratios = json.load(fh)

    for reaction, branch_ratios in all_branch_ratios.items():
        chain.set_branch_ratios(
            branch_ratios=branch_ratios, reaction=reaction, strict=False
        )

    # Export to new XML file
    chain.export_to_xml(chain_out)
    print(f"written {chain_out}")


def main():
    update_chain(args.chain_in, args.branching_ratios, args.chain_out)


if __name__ == "__main__":
    main()
