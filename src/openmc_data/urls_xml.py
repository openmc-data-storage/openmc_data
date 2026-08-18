all_chain_release_details = {
    "endf": {
        "b7.1": {
            "None": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b7.1.xml"
                }
            },
            "SFR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b7.1_sfr.xml"
                }
            },
            "PWR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b7.1_pwr.xml"
                }
            }
        },
        "b8.0": {
            "None": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b8.0.xml"
                }
            },
            "SFR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b8.0_sfr.xml"
                }
            },
            "PWR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b8.0_pwr.xml"
                }
            },
        },
        "b8.1": {
            "None": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b8.1.xml"
                }
            },
            "SFR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b8.1_sfr.xml"
                }
            },
            "PWR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_endf_b8.1_pwr.xml"
                }
            },
        }
    },
    # The tendl chains use decay data and neutron induced fission yields from
    # ENDF/B-VIII.0 and are all made with generate_tendl_chain, so the releases
    # can be compared against each other.
    #
    # FNS is a fusion neutron source spectrum. These branching ratios for the
    # production of metastable states are made with generate_branching_ratios,
    # which collapses the isomeric production data in the TENDL files with a
    # spectrum from the IAEA CoNDERC FNS benchmark.
    #
    # FNS-ORIGEN is the earlier chain hosted on the openmc_activator repository.
    # Its branching ratios come from ORIGEN rather than from TENDL, so it is kept
    # available but is not the TENDL only option.
    "tendl": {
        "2017": {
            "None": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2017_endf80.xml"
                }
            },
            "SFR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2017_endf80_sfr.xml"
                }
            },
            "PWR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2017_endf80_pwr.xml"
                }
            },
            "FNS": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2017_endf80_fns.xml"
                }
            },
            "FNS-ORIGEN": {
                "chain": {
                    "url": "https://github.com/jbae11/openmc_activator/raw/refs/heads/main/chain_tendl_2017_endf80_fns_flux.xml"
                }
            }
        },
        "2019": {
            "None": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2019_endf80.xml"
                }
            },
            "SFR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2019_endf80_sfr.xml"
                }
            },
            "PWR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2019_endf80_pwr.xml"
                }
            },
            "FNS": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2019_endf80_fns.xml"
                }
            },
            "FNS-ORIGEN": {
                "chain": {
                    "url": "https://github.com/jbae11/openmc_activator/raw/refs/heads/main/fns_spectrum.chain.xml"
                }
            }
        },
        "2025": {
            "None": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2025_endf80.xml"
                }
            },
            "SFR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2025_endf80_sfr.xml"
                }
            },
            "PWR": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2025_endf80_pwr.xml"
                }
            },
            "FNS": {
                "chain": {
                    "url": "https://github.com/openmc-data-storage/openmc_data/raw/main/src/openmc_data/depletion/chain_tendl_2025_endf80_fns.xml"
                }
            }
        }
    }
}
