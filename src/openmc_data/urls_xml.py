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
    # the tendl chains use decay data and neutron induced fission yields from
    # ENDF/B-VIII.0. The FNS (fusion neutron source) chains are hosted on the
    # openmc_activator repository as the flux collapsed branching ratios to
    # metastable states can not currently be reproduced by this package.
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
                    "url": "https://github.com/jbae11/openmc_activator/raw/refs/heads/main/chain_tendl_2017_endf80_fns_flux.xml"
                }
            }
        },
        "2019": {
            "FNS": {
                "chain": {
                    "url": "https://github.com/jbae11/openmc_activator/raw/refs/heads/main/fns_spectrum.chain.xml"
                }
            }
        }
    }
}
