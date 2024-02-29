all_decay_release_details = {
    'endf': {
            'b7.1': {
                'neutron': {
                    'base_url': ['https://www.nndc.bnl.gov/endf-b7.1/zips/'],
                    'compressed_files': ['ENDF-B-VII.1-neutrons.zip'],
                },
                'decay': {
                    'base_url': ['https://www.nndc.bnl.gov/endf-b7.1/zips/'],
                    'compressed_files': ['ENDF-B-VII.1-decay.zip']
                },
                'nfy': {
                    'base_url': ['https://www.nndc.bnl.gov/endf-b7.1/zips/'],
                    'compressed_files': ['ENDF-B-VII.1-nfy.zip']
                }
            },
            'b8.0': {
                'neutron': {
                    'base_url': ['https://www.nndc.bnl.gov/endf-b8.0/zips/'],
                    'compressed_files': ['ENDF-B-VIII.0_neutrons.zip'],
                },
                'decay': {
                    'base_url': ['https://www.nndc.bnl.gov/endf-b8.0/zips/'],
                    'compressed_files': ['ENDF-B-VIII.0_decay.zip']
                },
                'nfy': {
                    'base_url': ['https://www.nndc.bnl.gov/endf-b8.0/zips/'],
                    'compressed_files': ['ENDF-B-VIII.0_nfy.zip']
                }
            }
        },
    'jeff': {
        '3.3': {
            'neutron': {
                'base_url': ['https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/'],
                'compressed_files': ['JEFF33-n.tgz']
            },
            'decay': {
                'base_url': ['https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/'],
                'compressed_files': ['JEFF33-rdd.zip']
            },
            'nfy': {
                'base_url': ['https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/'],
                'compressed_files': ['JEFF33-nfy.asc']
            }       
        }
    },
    'tendl': {
        '2015': {
            'neutron':{
                'base_url': 'https://tendl.web.psi.ch/tendl_2015/tar_files/',
                'compressed_files': ['TENDL-n.tgz'],
            }
        },
        '2017': {
            'neutron':{
                'base_url': 'https://tendl.web.psi.ch/tendl_2017/tar_files/',
                'compressed_files': ['TENDL-n.tgz'],
            }
        },
        '2019': {
            'neutron':{
                'base_url': 'https://tendl.web.psi.ch/tendl_2019/tar_files/',
                'compressed_files': ['TENDL-n.tgz'],
            }
        },
        '2021': {
            'neutron':{
                'base_url': 'https://tendl.web.psi.ch/tendl_2021/tar_files/',
                'compressed_files': ['TENDL-n.tgz'],
            }
        }
    },
    'jendl': {
        '5.0': {
            'neutron': {
                'base_url': 'https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/',
                'compressed_files': ['jendl5-n.tar.gz', 'jendl5-n_upd1.tar.gz',
                                        'jendl5-n_upd6.tar.gz', 'jendl5-n_upd7.tar.gz',
                                        'jendl5-n_upd10.tar.gz', 'jendl5-n_upd11.tar.gz',
                                        'jendl5-n_upd12.tar.gz'],
                'endf_files': 'jendl5-n/*.dat',
                'errata': ['jendl5-n_upd1/*.dat', 'jendl-n_upd6/*.dat', '*.dat'],
            },
            'decay': {
                'base_url': ['https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/'],
                'compressed_files': ['jendl5-dec_upd5.tar.gz'],
                'decay_files': 'jendl5-dec_upd5/*.dat' 
            },
            'nfy': {
                'base_url': ['https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/'],
                'compressed_files': ['jendl5-fpy_upd8.tar.gz'],
                'nfy_files': 'jendl5-fpy_upd8/*.dat'
            }       
        }
    }
}
