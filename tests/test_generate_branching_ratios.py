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


def test_state_without_an_isomer_in_decay_data_is_ground(module):
    # Tb156 as TENDL-2025 gives it: the 88.4 keV state is Tb156_m2 and the
    # 200.1 keV state has no isomer in the ENDF/B-VIII.0 decay data
    evaluation = mf8([(65156, 0.0, 0), (65156, 88400.0, 3), (65156, 200100.0, 9)])
    isomers = {(65, 156): {1: 69600.0, 2: 88400.0}}
    targets = module.isomer_targets(evaluation, 102, isomers)
    assert names(targets) == {0: "Tb156", 3: "Tb156_m2", 9: "Tb156"}


def test_nearest_state_takes_a_shared_isomer(module):
    # Tl186 in TENDL-2025: states at 120 and 494 keV, one 374 keV isomer
    evaluation = mf8([(81186, 0.0, 0), (81186, 120000.0, 1), (81186, 494000.0, 2)])
    isomers = {(81, 186): {1: 374000.0}}
    targets = module.isomer_targets(evaluation, 102, isomers)
    assert names(targets) == {0: "Tl186", 1: "Tl186", 2: "Tl186_m1"}


def test_rates_of_states_counted_as_ground_are_summed(module):
    targets = {0: ("Tb156", 10), 3: ("Tb156_m2", 10), 9: ("Tb156", 10)}
    ratios = module.ratios_by_target(targets, {0: 2.0, 3: 1.0, 9: 1.0})
    assert ratios == pytest.approx({"Tb156": 0.75, "Tb156_m2": 0.25})


def test_several_isomers_are_matched_by_energy(module):
    evaluation = mf8([(73182, 0.0, 0), (73182, 16000.0, 1), (73182, 519577.0, 2)])
    targets = module.isomer_targets(evaluation, 102, TA182_ISOMERS)
    assert names(targets) == {0: "Ta182", 1: "Ta182_m1", 2: "Ta182_m2"}
