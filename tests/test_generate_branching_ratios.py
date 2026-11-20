"""Offline tests for how generate_branching_ratios names the isomeric states."""

import importlib
import sys
from types import SimpleNamespace

import pytest

pytest.importorskip("openmc")


@pytest.fixture(scope="module")
def module():
    # the arguments are parsed on import, so give it a valid command line
    argv = sys.argv
    sys.argv = ["generate_branching_ratios", "-n", ".", "--flux", "flux.txt"]
    try:
        yield importlib.import_module("openmc_data.depletion.generate_branching_ratios")
    finally:
        sys.argv = argv


def number(value):
    if isinstance(value, int):
        return f"{value:11d}"
    mantissa, exponent = f"{value:.6e}".split("e")
    return f"{mantissa}{int(exponent):+d}".rjust(11)


def mf8(states, mt=102):
    """An MF=8 section with one CONT record per (ZA, excitation energy, LFS)."""
    def record(values):
        return "".join(number(v) for v in values) + f"7328 8{mt:3d}    1\n"
    text = record([73181, 180.0, 0, 0, len(states), 1])
    for za, energy, lfs in states:
        text += record([float(za), energy, 10, lfs, 0, 0])
    return SimpleNamespace(section={(8, mt): text})


# Ta181 capture as JEFF-4.0 gives it: the ground state and the 519.6 keV
# isomer, which is Ta182_m2 as the 16.3 keV Ta182_m1 is not listed
TA182 = mf8([(73182, 0.0, 0), (73182, 519577.0, 2)])
TA182_ISOMERS = {(73, 182): {1: 16263.0, 2: 519572.0}}


def names(targets):
    return {lfs: name for lfs, (name, _lmf) in targets.items()}


def test_ranking_without_decay_data(module):
    assert names(module.isomer_targets(TA182, 102)) == {0: "Ta182", 2: "Ta182_m1"}


def test_decay_data_matches_the_listed_isomer(module):
    targets = module.isomer_targets(TA182, 102, TA182_ISOMERS)
    assert names(targets) == {0: "Ta182", 2: "Ta182_m2"}


def test_unknown_isomer_energy_falls_back_to_ranking(module):
    isomers = {(73, 182): {1: 0.0, 2: 519572.0}}
    assert names(module.isomer_targets(TA182, 102, isomers)) == {0: "Ta182", 2: "Ta182_m1"}


def test_product_without_isomers_in_decay_data_is_ranked(module):
    isomers = {(72, 177): {1: 1315450.0, 2: 2740000.0}}
    assert names(module.isomer_targets(TA182, 102, isomers)) == {0: "Ta182", 2: "Ta182_m1"}


def test_two_states_matching_one_isomer_is_ambiguous(module):
    evaluation = mf8([(73182, 0.0, 0), (73182, 500000.0, 1), (73182, 519577.0, 2)])
    assert module.isomer_targets(evaluation, 102, TA182_ISOMERS) is None


def test_several_isomers_are_matched_by_energy(module):
    evaluation = mf8([(73182, 0.0, 0), (73182, 16000.0, 1), (73182, 519577.0, 2)])
    targets = module.isomer_targets(evaluation, 102, TA182_ISOMERS)
    assert names(targets) == {0: "Ta182", 1: "Ta182_m1", 2: "Ta182_m2"}
