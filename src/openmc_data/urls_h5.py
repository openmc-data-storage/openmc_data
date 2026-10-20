all_h5_release_details = {
    "endf": {
        "b7.1": {
            "neutron-photon": {
                "base_url": "https://anl.box.com/shared/static/",
                "compressed_files": ["9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz"],
                "compressed_file_size": 1.6,
                "uncompressed_file_size": 6.2,
            }
        },
        "b8.0": {
            "neutron-photon": {
                "base_url": "https://anl.box.com/shared/static/",
                "compressed_files": ["uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz"],
                "compressed_file_size": 3.4,
                "uncompressed_file_size": 13.7,
            }
        },
        "b8.1": {
            "neutron-photon": {
                "base_url": "https://anl.box.com/shared/static/",
                "compressed_files": ["6qr7jezzihkj9p9esl5jn19qgpujyjyz.xz"],
                "compressed_file_size": 3.4,
                "uncompressed_file_size": 13.7,
            }
        },
    },
    # Official OpenMC libraries: https://openmc.org/data/#official-data-libraries
    # These include JEFF neutron/thermal data and ENDF/B photon supplements,
    # not the older NEA-converted JEFF 3.3 library. Sizes are not recorded.
    "jeff": {
        "3.3": {
            "neutron-photon": {
                "base_url": "https://anl.box.com/shared/static/",
                "compressed_files": ["4jwkvrr9pxlruuihcrgti75zde6g7bum.xz"],
            }
        },
        "4.0": {
            "neutron-photon": {
                "base_url": "https://anl.box.com/shared/static/",
                "compressed_files": ["fmcr8zoox1t6um0rwb2iw1nz72xue8ol.xz"],
            }
        },
    },
    "tendl": {
        "2019": {
            "neutron": {
                "base_url": "https://tendl.imperial.ac.uk/tendl_2019/tar_files/",
                "compressed_files": ["tendl19_hdf5.tar.bz2"],
                "compressed_file_size": 1.3,
                "uncompressed_file_size": 2.5,
            }
        },
        "2021": {
            "neutron": {
                "base_url": "https://tendl.imperial.ac.uk/tendl_2021/tar_files/",
                "compressed_files": ["tendl21_hdf5.tar.bz2"],
                "compressed_file_size": 1.3,
                "uncompressed_file_size": 2.5,
            }
        },
    }
}
