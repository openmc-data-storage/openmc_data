all_release_details = {
    "tendl": {
        "2015": {
            "neutron": {
                "ace": {
                    "base_url": "https://tendl.web.psi.ch/tendl_2015/tar_files/",
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
                    "base_url": "https://tendl.web.psi.ch/tendl_2017/tar_files/",
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
                    "base_url": "https://tendl.web.psi.ch/tendl_2019/tar_files/",
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
                    "base_url": "https://tendl.web.psi.ch/tendl_2021/tar_files/",
                    "compressed_files": ["tendl21c.tar.bz2"],
                    "neutron_files": "tendl21c/*",
                    "metastables": "tendl21c/*m",
                    "compressed_file_size": 2.2,
                    "uncompressed_file_size": 10.5,
                }
            }
        },
    },
    "fendl": {
        "3.2c": {
            "neutron": {
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl/data/neutron/",
                    "compressed_files": ["fendl-FENDL-3.2c-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "ace": {
                    "base_url": "https://www-nds.iaea.org/fendl/data/neutron/",
                    "compressed_files": ["fendl-FENDL-3.2c-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32b/data/neutron/",
                    "compressed_files": ["fendl-3.2b-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "ace": {
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32b/data/neutron/",
                    "compressed_files": ["fendl-3.2b-neutron-ace.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32b/data/atom/",
                    "compressed_files": ["fendl-3.2b-atom-endf.zip"],
                    "endf_files": "photon/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
        },
        "3.2a": {
            "neutron": {
                "ace": {
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32a/data/neutron/",
                    "compressed_files": ["fendl32-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*[!.xsd]",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32a/data/neutron/",
                    "compressed_files": ["fendl32-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32a/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32/data/neutron/",
                    "compressed_files": ["fendl32-neutron-ace.zip"],
                    "ace_files": "neutron/ace/*[!.xsd]",
                    "compressed_file_size": 0.565,
                    "uncompressed_file_size": 4.226,
                },
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32/data/neutron/",
                    "compressed_files": ["fendl32-neutron-endf.zip"],
                    "endf_files": "neutron/endf/*.endf",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf":{
                    "base_url": "https://www-nds.iaea.org/fendl_library/websites/fendl32/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl31d/data/neutron/",
                    "compressed_files": ["fendl31d-neutron-ace.zip"],
                    "ace_files": "fendl31d_ACE/*",
                    "compressed_file_size": 0.425,
                    "uncompressed_file_size": 2.290,
                },
                "endf":{
                    "base_url": "https://www-nds.iaea.org/fendl31d/data/neutron/",
                    "compressed_files": ["fendl31d-neutron-endf.zip"],
                    "endf_files": "*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl31d/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl31a-neutron-ace.zip"],
                    "ace_files": "*[0-9]",
                    "compressed_file_size": 0.384,
                    "uncompressed_file_size": 2.250,
                },
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl31a-neutron-endf.zip"],
                    "endf_files": "*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf":{
                    "base_url": "https://www-nds.iaea.org/fendl31/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl31a-neutron-ace.zip"],
                    "ace_files": "*[0-9]",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                },
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl31/data/neutron/",
                    "compressed_files": ["fendl30-neutron-endf.zip"],
                    "endf_files": "*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf":{
                    "base_url": "https://www-nds.iaea.org/fendl31/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl30/data/neutron/",
                    "compressed_files": ["fendl30-neutron-ace.zip"],
                    "ace_files": "ace/*.ace",
                    "compressed_file_size": 0.364,
                    "uncompressed_file_size": 2.200,
                },
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl30/data/neutron/",
                    "compressed_files": ["fendl30-neutron-endf.zip"],
                    "endf_files": "endf/*.txt",
                    "compressed_file_size": 0,
                    "uncompressed_file_size": 0,
                }
            },
            "photon": {
                "endf": {
                    "base_url": "https://www-nds.iaea.org/fendl30/data/atom/",
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
                    "base_url": "https://www-nds.iaea.org/fendl21/fendl21mc/",
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
                    "base_url": "https://www-nds.iaea.org/fendl21/fendl21e/",
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
                    "base_url": "https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_32/Processed/",
                    "compressed_files": [
                        "JEFF32-ACE-293K.tar.gz",
                        "JEFF32-ACE-400K.tar.gz",
                        "JEFF32-ACE-500K.tar.gz",
                        "JEFF32-ACE-600K.tar.gz",
                        "JEFF32-ACE-700K.tar.gz",
                        "JEFF32-ACE-800K.zip",  # Note the different suffix
                        "JEFF32-ACE-900K.tar.gz",
                        "JEFF32-ACE-1000K.tar.gz",
                        "JEFF32-ACE-1200K.tar.gz",
                        "JEFF32-ACE-1500K.tar.gz",
                        "JEFF32-ACE-1800K.tar.gz",
                        "TSLs.tar.gz"],
                    "temperatures": [
                        "293",
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
                        None
                    ],
                    "neutron_files": "*.ACE",
                    "metastables": "*M.ACE",
                    "sab_files": "ANNEX_6_3_STLs/*/*.ace",
                    "redundant": "ACEs_293K/*-293.ACE",
                    "compressed_file_size": 9,
                    "uncompressed_file_size": 40,
                }
            }
        },
        "3.3": {
            'neutron': {
                'ace': {
                    "base_url": "http://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/temperatures/",
                    "compressed_files": [
                        "ace_293.tar.gz",
                        "ace_600.tar.gz",
                        "ace_900.tar.gz",
                        "ace_1200.tar.gz",
                        "ace_1500.tar.gz",
                        "ace_1800.tar.gz",
                        "ace_tsl.tar.gz",
                    ],
                    "temperatures": [
                        "293",
                        "600",
                        "900",
                        "1200",
                        "1500",
                        "1800",
                        None
                    ],
                    "neutron_files": "ace_293/*.ace",
                    "thermal_files": "ace_tsl",
                    "compressed_file_size": 7.7,
                    "uncompressed_file_size": 37,
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
                    'compressed_files': ['jendl5-n.tar.gz', 'jendl5-n_upd1.tar.gz',
                                         'jendl5-n_upd6.tar.gz', 'jendl5-n_upd7.tar.gz',
                                         'jendl5-n_upd10.tar.gz', 'jendl5-n_upd11.tar.gz',
                                         'jendl5-n_upd12.tar.gz'],
                    'endf_files': 'jendl5-n/*.dat',
                    'errata': ['jendl5-n_upd1/*.dat', 'jendl-n_upd6/*.dat', '*.dat'],
                    'metastables': 'jendl5-n/*m1.dat',
                    'compressed_file_size': 4.1,
                    'uncompressed_file_size': 16
                }
            }
        }
    }
}
