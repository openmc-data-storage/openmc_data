all_release_details = {
    "tendl": {
        "2015": {
            "neutron": {
                "ace": {
                    "base_url": "https://tendl.imperial.ac.uk/tendl_2015/tar_files/",
                    "compressed_files": ["ACE-n.tgz"],
                    "neutron_files": "neutron_file/*/*/lib/endf/*-n.ace",
                    "metastables": "neutron_file/*/*/lib/endf/*m-n.ace",
                    "compressed_file_size": 5.1,
                    "uncompressed_file_size": 40,
                }
            }
        },
        "2017": {
            "neutron": {
                "ace":{
                    "base_url": "https://tendl.imperial.ac.uk/tendl_2017/tar_files/",
                    "compressed_files": ["tendl17c.tar.bz2"],
                    "neutron_files": "ace-17/*",
                    "metastables": "ace-17/*m",
                    "compressed_file_size": 2.1,
                    "uncompressed_file_size": 14,
                }
            }
        },
        "2019": {
            "neutron": {
                "ace": {
                    "base_url": "https://tendl.imperial.ac.uk/tendl_2019/tar_files/",
                    "compressed_files": ["tendl19c.tar.bz2"],
                    "neutron_files": "tendl19c/*",
                    "metastables": "tendl19c/*m",
                    "compressed_file_size": 2.3,
                    "uncompressed_file_size": 10.1,
                }
            }
        },
        "2021": {
            "neutron": {
                "ace": {
                    "base_url": "https://tendl.imperial.ac.uk/tendl_2021/tar_files/",
                    "compressed_files": ["tendl21c.tar.bz2"],
                    "neutron_files": "tendl21c/*",
                    "metastables": "tendl21c/*m",
                    "compressed_file_size": 2.2,
                    "uncompressed_file_size": 10.5,
                }
            }
        },
        "2023": {
            "neutron": {
                "endf": {
                    "base_url": "https://tendl.imperial.ac.uk/tendl_2023/tar_files/",
                    "compressed_files": ["TENDL-n.2024new.tgz"],
                    "endf_files": "n-*.tendl",
                    "metastables": "n-*m.tendl",
                    "compressed_file_size": 3.5,
                    "uncompressed_file_size": 20,
                }
            }
        },
        "2025": {
            "neutron": {
                "endf": {
                    "base_url": "https://tendl.imperial.ac.uk/tendl_2025/tar_files/",
                    "compressed_files": ["TENDL-n.tgz"],
                    "endf_files": "n-*.tendl",
                    "metastables": "n-*m.tendl",
                    "compressed_file_size": 3.1,
                    "uncompressed_file_size": 13.9,
                }
            }
        },
    },
    "fendl": {
        "3.2c": {
            "neutron": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl/data/neutron/",
                    "compressed_files": ["fendl-FENDL-3.2c-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl/data/neutron/",
                    "compressed_files": ["fendl-FENDL-3.2c-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl/data/atom/",
                    "compressed_files": ["fendl-FENDL-3.2c-atom-endf.zip"],
                    "endf_files": "atom/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
        },
        "3.2b": {
            "neutron": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32b/data/neutron/",
                    "compressed_files": ["fendl-3.2b-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32b/data/neutron/",
                    "compressed_files": ["fendl-3.2b-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32b/data/atom/",
                    "compressed_files": ["fendl-3.2b-atom-endf.zip"],
                    "endf_files": "atom/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
        },
        "3.2a": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32a/data/neutron/",
                    "compressed_files": ["fendl32-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*[!.xsd]",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32a/data/neutron/",
                    "compressed_files": ["fendl32-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32a/data/atom/",
                    "compressed_files": ["fendl32-atom-endf.zip"],
                    "endf_files": "atom/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            }
        },
        "3.2": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32/data/neutron/",
                    "compressed_files": ["fendl32-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*[!.xsd]",
                    "compressed_file_size": 0.565,
                    "uncompressed_file_size": 4.226,
                },
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32/data/neutron/",
                    "compressed_files": ["fendl32-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf":{
                    "base_url": "https://nds.iaea.org/fendl_library/websites/fendl32/data/atom/",
                    "compressed_files": ["fendl32-atom-endf.zip"],
                    "endf_files": "atom/endf/*.endf",
                    "compressed_file_size": 0.004,
                    "uncompressed_file_size": 0.033,
                }
            },
        },
        "3.1d": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl31d/data/neutron/",
                    "compressed_files": ["fendl31d-neutron-ace.zip"],
                    "ace_files": "fendl31d_ACE/*",
                    "compressed_file_size": 0.425,
                    "uncompressed_file_size": 2.290,
                },
                "endf":{
                    "base_url": "https://nds.iaea.org/fendl31d/data/neutron/",
                    "compressed_files": ["fendl31d-neutron-endf.zip"],
                    "endf_files": "*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl31d/data/atom/",
                    "compressed_files": ["fendl30-atom-endf.zip"],
                    "endf_files": "endf/*.txt",
                    "compressed_file_size": 0.004,
                    "uncompressed_file_size": 0.012,
                }
            },
        },
        # NOTE 3.1a appears to have has the website removed, url appears to still work
        "3.1a": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl31a-neutron-ace.zip"],
                    "ace_files": "*[0-9]",
                    "compressed_file_size": 0.384,
                    "uncompressed_file_size": 2.250,
                },
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl31a-neutron-endf.zip"],
                    "endf_files": "*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf":{
                    "base_url": "https://nds.iaea.org/fendl31/data/atom/",
                    "compressed_files": ["fendl30-atom-endf.zip"],
                    "endf_files": "endf/*.txt",
                    "compressed_file_size": 0.004,
                    "uncompressed_file_size": 0.012,
                }
            },
        },
        "3.1": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl31a-neutron-ace.zip"],
                    "ace_files": "*[0-9]",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl30-neutron-endf.zip"],
                    "endf_files": "*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf":{
                    "base_url": "https://nds.iaea.org/fendl31/data/atom/",
                    "compressed_files": ["fendl30-atom-endf.zip"],
                    "endf_files": "endf/*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
        },
        "3.0": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl30/data/neutron/",
                    "compressed_files": ["fendl30-neutron-ace.zip"],
                    "ace_files": "ace/*.ace",
                    "compressed_file_size": 0.364,
                    "uncompressed_file_size": 2.200,
                },
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl30/data/neutron/",
                    "compressed_files": ["fendl30-neutron-endf.zip"],
                    "endf_files": "endf/*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl30/data/atom/",
                    "compressed_files": ["fendl30-atom-endf.zip"],
                    "endf_files": "endf/*.txt",
                    "compressed_file_size": 0.004,
                    "uncompressed_file_size": 0.012,
                }
            },
        },
        "2.1": {
            "neutron": {
                "ace": {
                    "base_url": "https://nds.iaea.org/fendl21/fendl21mc/",
                    "compressed_files": [
                        "H001mc.zip",
                        "H002mc.zip",
                        "H003mc.zip",
                        "He003mc.zip",
                        "He004mc.zip",
                        "Li006mc.zip",
                        "Li007mc.zip",
                        "Be009mc.zip",
                        "B010mc.zip",
                        "B011mc.zip",
                        "C012mc.zip",
                        "N014mc.zip",
                        "N015mc.zip",
                        "O016mc.zip",
                        "F019mc.zip",
                        "Na023mc.zip",
                        "Mg000mc.zip",
                        "Al027mc.zip",
                        "Si028mc.zip",
                        "Si029mc.zip",
                        "Si030mc.zip",
                        "P031mc.zip",
                        "S000mc.zip",
                        "Cl035mc.zip",
                        "Cl037mc.zip",
                        "K000mc.zip",
                        "Ca000mc.zip",
                        "Ti046mc.zip",
                        "Ti047mc.zip",
                        "Ti048mc.zip",
                        "Ti049mc.zip",
                        "Ti050mc.zip",
                        "V000mc.zip",
                        "Cr050mc.zip",
                        "Cr052mc.zip",
                        "Cr053mc.zip",
                        "Cr054mc.zip",
                        "Mn055mc.zip",
                        "Fe054mc.zip",
                        "Fe056mc.zip",
                        "Fe057mc.zip",
                        "Fe058mc.zip",
                        "Co059mc.zip",
                        "Ni058mc.zip",
                        "Ni060mc.zip",
                        "Ni061mc.zip",
                        "Ni062mc.zip",
                        "Ni064mc.zip",
                        "Cu063mc.zip",
                        "Cu065mc.zip",
                        "Ga000mc.zip",
                        "Zr000mc.zip",
                        "Nb093mc.zip",
                        "Mo092mc.zip",
                        "Mo094mc.zip",
                        "Mo095mc.zip",
                        "Mo096mc.zip",
                        "Mo097mc.zip",
                        "Mo098mc.zip",
                        "Mo100mc.zip",
                        "Sn000mc.zip",
                        "Ta181mc.zip",
                        "W182mc.zip",
                        "W183mc.zip",
                        "W184mc.zip",
                        "W186mc.zip",
                        "Au197mc.zip",
                        "Pb206mc.zip",
                        "Pb207mc.zip",
                        "Pb208mc.zip",
                        "Bi209mc.zip",
                    ],
                    "ace_files": "*.ace",
                    "compressed_file_size": 0.100,
                    "uncompressed_file_size": 0.600,
                },
            },
            "photon": {
                "endf": {
                    "base_url": "https://nds.iaea.org/fendl21/fendl21e/",
                    "compressed_files": ["FENDLEP.zip"],
                    "endf_files": "*.endf",
                    "compressed_file_size": 0.002,
                    "uncompressed_file_size": 0.005,
                }
            },
        },
    },
    'endf': {
        "b7.1": {
            "neutron": {
                "ace": {
                    "base_url": "http://www.nndc.bnl.gov/endf-b7.1/aceFiles/",
                    "compressed_files": [
                        "ENDF-B-VII.1-neutron-293.6K.tar.gz",
                        "ENDF-B-VII.1-tsl.tar.gz",
                    ],
                    "checksums": [
                        "9729a17eb62b75f285d8a7628ace1449",
                        "e17d827c92940a30f22f096d910ea186",
                    ],
                    "ace_files": "[aA-zZ]*.ace",
                    "sab_files": "*.acer",
                    "compressed_file_size": 0.497,
                    "uncompressed_file_size": 1.200,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "http://www.nndc.bnl.gov/endf-b7.1/zips/",
                    "compressed_files": [
                        "ENDF-B-VII.1-photoat.zip",
                        "ENDF-B-VII.1-atomic_relax.zip",
                    ],
                    "checksums": [
                        "5192f94e61f0b385cf536f448ffab4a4",
                        "fddb6035e7f2b6931e51a58fc754bd10",
                    ],
                    "photo_files": "photoat/*.endf",
                    "atom_files": "atomic_relax/*.endf",
                    "compressed_file_size": 0.009,
                    "uncompressed_file_size": 0.045,
                }
            },
        }
    },
    'jeff': {
        "3.2": {
            'neutron': {
                "ace":{
                    "base_url": "https://data.oecd-nea.org/api/records/8wvwt-vgy24/files/",
                    "url_suffix": "/content",
                    "as_browser": True,
                    "compressed_files": [f"JEFF32-ACE-{t}K.tar.gz" for t in
                                         (293, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 1800)],
                    "temperatures": [
                        "293",
                        "300",
                        "400",
                        "500",
                        "600",
                        "700",
                        "800",
                        "900",
                        "1000",
                        "1200",
                        "1500",
                        "1800",
                    ],
                    "compressed_file_size": 9,
                    "uncompressed_file_size": 40,
                }
            },
            'thermal': {
                'ace': {
                    "base_url": "https://data.oecd-nea.org/api/records/z2s35-csq77/files/",
                    "url_suffix": "/content",
                    "as_browser": True,
                    "compressed_files": ["JEFF32-Processed-ACE-TSL.zip"],
                    "ace_paths": ["TSL-ACE/**/*.ace", "ANNEX_6_3_STLs/**/*.ace"],
                    "compressed_file_size": 0.06,
                    "uncompressed_file_size": 0.3,
                }
            }
        },
        "3.3": {
            'neutron': {
                'ace': {
                    "base_url": "https://data.oecd-nea.org/api/records/zjcaq-2rw89/files/",
                    "url_suffix": "/content",
                    "as_browser": True,
                    "compressed_files": [f"ace_{t}.tar.gz" for t in (293, 600, 900, 1200, 1500, 1800)],
                    "temperatures": ["293", "600", "900", "1200", "1500", "1800"],
                    "compressed_file_size": 7.7,
                    "uncompressed_file_size": 37,
                }
            },
            'thermal': {
                'ace': {
                    "base_url": "https://data.oecd-nea.org/api/records/1rkw4-zk241/files/",
                    "url_suffix": "/content",
                    "as_browser": True,
                    "compressed_files": ["ace_tsl.tar.gz"],
                    "ace_paths": ["ace_tsl/*.ace"],
                    "required_file_groups": [
                        "al-sap", "be", "ca-cah2", "d-d2o", "graph", "h-cah2",
                        "h-ch2", "h-h2o", "h-ice", "h-zrh", "mesi", "mg",
                        "o-d2o", "orto-d", "orto-h", "o-sap", "para-d",
                        "para-h", "sili", "tolu",
                    ],
                    "compressed_file_size": 0.93,
                    "uncompressed_file_size": 5,
                }
            }
        },
        "4.0": {
            'neutron': {
                'ace': {
                    "base_url": "https://data.oecd-nea.org/api/records/0vhn5-d6t91/files/",
                    "url_suffix": "/content",
                    "as_browser": True,
                    "compressed_files": [f"JEFF40-Processed-Neutron-ACE-{t}K.zip" for t in
                                         ("0.1", "293", "300", "600", "900", "1200", "1500", "1800")],
                    "temperatures": ["0.1", "293", "300", "600", "900", "1200", "1500", "1800"],
                    "compressed_file_size": 0,  # Size estimate not available.
                    "uncompressed_file_size": 0,
                }
            },
            'thermal': {
                'ace': {
                    "base_url": "https://data.oecd-nea.org/api/records/m3qef-tjx77/files/",
                    "url_suffix": "/content",
                    "as_browser": True,
                    "compressed_files": ["JEFF40-Processed-TSL-selected-ACE.zip"],
                    "ace_paths": ["data/*"],
                    # Public convenience subset, NOT the complete JEFF-4.0 TSL library.
                    "selected_cases": 12,
                    "selected_tables": 316,
                    "compressed_file_size": 4.39,
                    "uncompressed_file_size": 0,  # Size estimate not available.
                }
            }
        }
    },
    'jendl': {
        '4.0': {
            'neutron': {
                'endf':{
                    'base_url': 'https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/',
                    'compressed_files': ['jendl40-or-up_20160106.tar.gz'],
                    'endf_files': 'jendl40-or-up_20160106/*.dat',
                    'metastables': 'jendl40-or-up_20160106/*m.dat',
                    'compressed_file_size': 0.2,
                    'uncompressed_file_size': 2
                }
            }
        },
        '5.0': {
            'neutron': {
                'endf':{
                    'base_url': 'https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/',
                    'compressed_files': ['jendl5-n.tar.gz'],
                    # Corrected evaluations, applied over jendl5-n in this order. See
                    # https://wwwndc.jaea.go.jp/jendl/j5/JENDL-5_Errata.html
                    'updates': ['jendl5-n_upd1.tar.gz',
                                'jendl5-n_upd6.tar.gz',
                                'jendl5-n_upd7.tar.gz',
                                'jendl5-n_upd10.tar.gz',
                                'jendl5-n_upd11.tar.gz',
                                'jendl5-n_upd12.tar.gz',
                                'jendl5-n_upd14.tar.gz',
                                'jendl5-n_upd17.tar.gz'],
                    'endf_files': 'jendl5-n/*.dat',
                    'metastables': 'jendl5-n/*m1.dat',
                    'compressed_file_size': 4.1,
                    'uncompressed_file_size': 16
                }
            },
            'thermal': {
                'endf': {
                    'base_url': 'https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/',
                    'compressed_files': ['jendl5-tsl.tar.gz'],
                    'checksums': ['4e49d8eae83fd7de237db8f321eade36'],
                    # (neutron evaluation, thermal scattering evaluation, OpenMC
                    # name), relative to the extracted files. The names are given
                    # because OpenMC would otherwise fuzzy match the JENDL labels:
                    # liquid and solid phases, and C and H in the same molecule,
                    # would share a name. The neutron evaluations match the
                    # principal scatterer AWR in MF=7 MT=4; natural Si and Zr use
                    # the most abundant isotope as ENDF/B does.
                    'sab_files': [
                        ('jendl5-n/n_013-Al-027.dat', 'jendl5-tsl/tsl_013_Al_027.dat', 'c_Al27'),
                        ('jendl5-n/n_026-Fe-056.dat', 'jendl5-tsl/tsl_026_Fe_056.dat', 'c_Fe56'),
                        ('jendl5-n/n_004-Be-009.dat', 'jendl5-tsl/tsl_Be-metal.dat', 'c_Be'),
                        ('jendl5-n/n_004-Be-009.dat', 'jendl5-tsl/tsl_BeinBeO.dat', 'c_Be_in_BeO'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_crystalline-graphite.dat', 'c_Graphite'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_reactor-graphite-10P.dat', 'c_Graphite_10p'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_reactor-graphite-30P.dat', 'c_Graphite_30p'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSiC.dat', 'c_C_in_SiC'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidBenzene.dat', 'c_C_in_C6H6_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidBenzene.dat', 'c_C_in_C6H6_solid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidEthanol.dat', 'c_C_in_C2H6O_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidEthanol.dat', 'c_C_in_C2H6O_solid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidMethane.dat', 'c_C_in_CH4_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidMethane.dat', 'c_C_in_CH4_solid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidMesitylene.dat', 'c_C_in_C9H12_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidMesitylene.dat', 'c_C_in_C9H12_solid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidM-Xylene.dat', 'c_C_in_C8H10_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidM-Xylene.dat', 'c_C_in_C8H10_solid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidToluene.dat', 'c_C_in_C7H8_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidToluene.dat', 'c_C_in_C7H8_solid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinLiquidTriphenylmethane.dat', 'c_C_in_C19H16_liquid'),
                        ('jendl5-n/n_006-C-012.dat', 'jendl5-tsl/tsl_CinSolidTriphenylmethane.dat', 'c_C_in_C19H16_solid'),
                        ('jendl5-n/n_001-H-002.dat', 'jendl5-tsl/tsl_DinD2O.dat', 'c_D_in_D2O'),
                        ('jendl5-n/n_001-H-002.dat', 'jendl5-tsl/tsl_DinOrthoD.dat', 'c_ortho_D'),
                        ('jendl5-n/n_001-H-002.dat', 'jendl5-tsl/tsl_DinParaD.dat', 'c_para_D'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinH2O.dat', 'c_H_in_H2O'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinIceIh.dat', 'c_H_in_H2O_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinCH2.dat', 'c_H_in_CH2'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinC5O2H8.dat', 'c_H_in_C5O2H8'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinYH2.dat', 'c_H_in_YH2'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinZrH.dat', 'c_H_in_ZrH'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinOrthoH.dat', 'c_ortho_H'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinParaH.dat', 'c_para_H'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidBenzene.dat', 'c_H_in_C6H6_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidBenzene.dat', 'c_H_in_C6H6_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidEthanol.dat', 'c_H_in_C2H6O_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidEthanol.dat', 'c_H_in_C2H6O_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidMethane.dat', 'c_H_in_CH4_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidMethane.dat', 'c_H_in_CH4_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidMesitylene.dat', 'c_H_in_C9H12_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidMesitylene.dat', 'c_H_in_C9H12_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidM-Xylene.dat', 'c_H_in_C8H10_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidM-Xylene.dat', 'c_H_in_C8H10_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidToluene.dat', 'c_H_in_C7H8_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidToluene.dat', 'c_H_in_C7H8_solid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinLiquidTriphenylmethane.dat', 'c_H_in_C19H16_liquid'),
                        ('jendl5-n/n_001-H-001.dat', 'jendl5-tsl/tsl_HinSolidTriphenylmethane.dat', 'c_H_in_C19H16_solid'),
                        ('jendl5-n/n_007-N-014.dat', 'jendl5-tsl/tsl_NinUN.dat', 'c_N_in_UN'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinBeO.dat', 'c_O_in_BeO'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinD2O.dat', 'c_O_in_D2O'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinH2O.dat', 'c_O_in_H2O'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinIceIh.dat', 'c_O_in_H2O_solid'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinUO2.dat', 'c_O_in_UO2'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinLiquidEthanol.dat', 'c_O_in_C2H6O_liquid'),
                        ('jendl5-n/n_008-O-016.dat', 'jendl5-tsl/tsl_OinSolidEthanol.dat', 'c_O_in_C2H6O_solid'),
                        ('jendl5-n/n_014-Si-028.dat', 'jendl5-tsl/tsl_SiinSiC.dat', 'c_Si_in_SiC'),
                        ('jendl5-n/n_014-Si-028.dat', 'jendl5-tsl/tsl_SiO2-alpha.dat', 'c_SiO2_alpha'),
                        ('jendl5-n/n_014-Si-028.dat', 'jendl5-tsl/tsl_SiO2-beta.dat', 'c_SiO2_beta'),
                        ('jendl5-n/n_092-U-238.dat', 'jendl5-tsl/tsl_UinUN.dat', 'c_U_in_UN'),
                        ('jendl5-n/n_092-U-238.dat', 'jendl5-tsl/tsl_UinUO2.dat', 'c_U_in_UO2'),
                        ('jendl5-n/n_039-Y-089.dat', 'jendl5-tsl/tsl_YinYH2.dat', 'c_Y_in_YH2'),
                        ('jendl5-n/n_040-Zr-090.dat', 'jendl5-tsl/tsl_ZrinZrH.dat', 'c_Zr_in_ZrH'),
                    ],
                    'compressed_file_size': 0.4,
                    'uncompressed_file_size': 1.3
                }
            },
            'photon': {
                'endf': {
                    'base_url': 'https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/',
                    'compressed_files': ['jendl5-pa.tar.gz', 'jendl5-ar.tar.gz'],
                    'checksums': ['50b5a159b80a105a8e4b6cf0d6832297',
                                  '71bf76621f12d132ae2e35fff98c8f77'],
                    'photo_files': 'jendl5-pa/*.dat',
                    'atom_files': 'jendl5-ar/*.dat',
                    'compressed_file_size': 0.04,
                    'uncompressed_file_size': 0.1
                }
            }
        }
    }
}
