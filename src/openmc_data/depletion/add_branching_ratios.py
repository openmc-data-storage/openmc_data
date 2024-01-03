import argparse
import json
from pathlib import Path

import openmc.deplete


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--chain_in', type=Path, required=True, help='Path of the input chain file')
parser.add_argument('-b', '--branching_ratios', type=Path, required=True, help='Path of the input branching ratios JSON file')
parser.add_argument('-o', '--chain_out', type=Path, required=True, help='Path of the produced chain file')
args = parser.parse_args()

def update_chain(chain_in, branching_ratios, chain_out):
    # Load existing chain
    chain = openmc.deplete.Chain.from_xml(chain_in)

    # Set branching ratios
    with open(branching_ratios) as fh:
        all_branch_ratios = json.load(fh)

    for reaction, branch_ratios in all_branch_ratios.items():

        chain.set_branch_ratios(
            branch_ratios=branch_ratios,
            reaction=reaction,
            strict=False
        )

    # Export to new XML file
    chain.export_to_xml(chain_out)

def main():
    update_chain(args.chain_in, args.branching_ratios, args.chain_out)

if __name__ == '__main__':
    main()
    
