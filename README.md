[![test_urls](https://github.com/shimwell/data/actions/workflows/test_urls.yml/badge.svg)](https://github.com/shimwell/data/actions/workflows/test_urls.yml)
[![test_package](https://github.com/openmc-data-storage/openmc_data/actions/workflows/test_package.yml/badge.svg)](https://github.com/openmc-data-storage/openmc_data/actions/workflows/test_package.yml)
[![test_convert_scripts](https://github.com/openmc-data-storage/openmc_data/actions/workflows/test_processing.yml/badge.svg)](https://github.com/openmc-data-storage/openmc_data/actions/workflows/test_processing.yml)


# OpenMC Data

Aims to facilitate the use of different nuclear data libraries with OpenMC by
providing command line tools that process and download nuclear data automatically.

# Prerequisites

You should have already installed OpenMC, see the [docs](https://docs.openmc.org/en/stable/quickinstall.html) for installation instructions.

# Installation

The package is distributed on [PYPI](https://pypi.org/project/openmc-data/) and can be installed with pip.

```bash
pip install openmc_data
```

# Usage

Once installed several scripts are available in your terminal that are able to
download and process nuclear data.

The scripts accept input arguments, to find out the input arguments available
for a particular script run the script name with ```--help``` after the name.
For example:

```convert_endf --help```

Some scripts (mainly the generate scripts) require [NJOY](https://github.com/njoy/NJOY2016) to be installed and
added to your path.

A few categories of scripts are available:
<ul>
<li>Scripts that produce h5 cross section files:</li>
<ul>
    <li>Convert ACE files to h5 files</li>
    <li>Generate h5 file from ENDF files</li>
    <li>Download h5 files</li>
</ul>
<li>Scripts that produce xml chain files:</li>
<ul>
    <li>Generate xml chain files from ENDF files:</li>
    <li>Download xml chain files:</li>
</ul>
<li>Other scripts that don't fall into either category.</li>
</ul>

## Produce Cross Section Files

### Convert cross sections

| Script name | Library | Release | Processed by |
|-|-|-|-|
|convert_mcnp70 | ENDF/B | VII.0 | LANL |
|convert_mcnp71 | ENDF/B | VII.1 | LANL |
|convert_endf | ENDF/B | VII.1 | NNDC |
|convert_lib80x | ENDF/B | VIII.0 | LANL |
|convert_fendl | FENDL | 3.2c<br>3.2b<br>3.2a<br>3.2<br>3.1d<br>3.1a<br>3.1<br>3.0<br>2.1 |
|convert_jeff32 | JEFF | 3.2 |
|convert_jeff33 | JEFF | 3.3 |
|convert_tendl | TENDL | 2015<br>2017<br>2019<br>2021 |

### Generate cross sections

| Script name | Library | Release | Processed by |
|-|-|-|-|
| generate_cendl | CENDL | 3.1<br>3.2 |  |
| generate_endf | ENDF/B | VII.1<br>VIII.0<br>VIII.1 | NNDC |
| generate_fendl | FENDL | 3.2c<br>3.2b<br>3.2a<br>3.2<br>3.1d<br>3.1a<br>3.0 | |
| generate_jendl | JENDL | 4.0<br>5.0 | |
| generate_tendl | TENDL | 2023<br>2025 | |


### Download cross sections

| Script name | Library | Release | Processed by |
|-|-|-|-|
| download_endf | ENDF/B | VII.1<br>VIII.0<br>VIII.1  | NNDC |
| download_tendl | TENDL | 2019<br>2021  |  |

<!-- | Script name | Library | Release | Processed by | Download available | Downloads ACE files and convert to HDF5 | Downloads ENDF files and convert to HDF5 | Convert local ACE files |
|-|-|-|-|-|-|-|-|
|generate_cendl| CENDL | 3.1<br>3.2 |  |  |  | :heavy_check_mark: |  |
|convert_mcnp70| ENDF/B | VII.0 | LANL | [openmc.org](https://anl.box.com/shared/static/t25g7g6v0emygu50lr2ych1cf6o7454b.xz) |  |  | :heavy_check_mark: |
|convert_mcnp71| ENDF/B | VII.1 | LANL | [openmc.org](https://anl.box.com/shared/static/d359skd2w6wrm86om2997a1bxgigc8pu.xz) |  |  | :heavy_check_mark: |
|generate_endf| ENDF/B | VII.1 | NNDC | [openmc.org](https://anl.box.com/shared/static/9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz) |  | :heavy_check_mark: |  |
|convert_endf| ENDF/B | VII.1 | NNDC | [openmc.org](https://anl.box.com/shared/static/9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz) | :heavy_check_mark: | :heavy_check_mark: |  |
|convert_lib80x| ENDF/B | VIII.0 | LANL | [openmc.org](https://anl.box.com/shared/static/nd7p4jherolkx4b1rfaw5uqp58nxtstr.xz) |  |  | :heavy_check_mark: |
|generate_endf| ENDF/B | VIII.0 | NNDC | [openmc.org](https://anl.box.com/shared/static/uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz) |  | :heavy_check_mark: |  |
|convert_fendl| FENDL | 2.1<br>3.0<br>3.1a<br>3.1d<br>3.2 |  | [openmc.org 3.2](https://anl.box.com/shared/static/3cb7jetw7tmxaw6nvn77x6c578jnm2ey.xz) | :heavy_check_mark: |  |  |
|generate_jendl| JENDL | 4.0 |  |  |  | :heavy_check_mark: |  |
|convert_jeff32| JEFF | 3.2 |  | [openmc.org](https://anl.box.com/shared/static/pb94oxriiipezysu7w4r2qdoufc2epxv.xz) | :heavy_check_mark: |  |  |
|convert_jeff33| JEFF | 3.3 |  | [openmc.org](https://anl.box.com/shared/static/ddetxzp0gv1buk1ev67b8ynik7f268hw.xz) | :heavy_check_mark: |  |  |
|convert_tendl| TENDL | 2015<br>2017<br>2019<br>2021|  |  | :heavy_check_mark: |  |  | -->

## Produce Depletion Chain files

### Generate chain files

| Script name | Library | Release |
|-|-|-|
|generate_endf_chain | ENDF/B | VII.1<br>VIII.0<br>VIII.1  |
|generate_jeff_chain | JEFF | 3.3  |
|generate_jendl_chain | JENDL | 5.0 |
|generate_tendl_chain | TENDL | 2015<br>2017<br>2019<br>2021<br>2023<br>2025 |
|generate_serpent_fissq | |  |
|generate_endf71_chain_casl | ENDF/B |  |

### Branching ratios for metastable states

Reactions can produce either the ground state or a metastable state of a
nuclide and the split between them is dependent on the neutron spectrum. The
`generate_branching_ratios` script finds this split from the isomeric production
data in the ENDF neutron files (MF=8 identifies the isomeric states and whether
the production data is in MF=9 or MF=10) and collapses it with a multigroup
neutron flux that you provide. The one group branching ratio is reaction rate
weighted, which is the weighting that preserves the production rate of each
isomer in a single energy group chain.

The JSON file produced is in the same format as the `branching_ratios_pwr.json`
and `branching_ratios_sfr.json` files, so it can be applied to a chain file with
`add_branching_ratios`.

```bash
# downloads the ENDF files and makes a chain file from them
generate_tendl_chain -r 2017 --lib endf80

# collapses the isomeric production data with a fusion neutron source spectrum
# taken from the IAEA CoNDERC FNS benchmark
generate_branching_ratios \
    --neutron-dir tendl-2017-endf/neutron \
    --fispact-fluxes fns/Ag/2000exp_5min_fluxes \
    --chain chain_tendl_2017_endf80.xml \
    --jobs 20 \
    -o branching_ratios_tendl_2017_fns.json

# adds the branching ratios to the chain file
add_branching_ratios \
    -i chain_tendl_2017_endf80.xml \
    -b branching_ratios_tendl_2017_fns.json \
    -o chain_tendl_2017_endf80_fns.xml
```

Most reactions store their isomeric production as cross sections in MF=10 and
need no other data. The remainder store multiplicities in MF=9 which have to be
weighted by the reaction cross section, and as the MF=3 cross section is only
the background in the resolved resonance range these are reconstructed with
NJOY. Passing `--cross-sections` will instead read them from an existing HDF5
library, which avoids the NJOY runs if you have already made one.

Only the shape of the cross section is used, as a weight, so the NJOY modules
that do not affect it are skipped and the reconstruction tolerance is loosened.
This is what makes the actinides tractable, as the unresolved resonance
probability tables take over two hours per nuclide, and it changes the branching
ratios by less than 0.2%.

Use `--jobs` to process files in parallel. A whole TENDL library is about 2800
evaluations and takes roughly half an hour with `--jobs 20`, against many hours
in series.

### Download chain files

| Script name | Library | Release | Branching options|
|-|-|-|-|
|download_chain | ENDF/B | VII.1<br>VIII.0<br>VIII.1 | None<br>SFR<br>PWR |
|download_chain | TENDL | 2017<br>2019 | None<br>SFR<br>PWR<br>FNS<br>FNS-ORIGEN |
|download_chain | TENDL | 2025 | None<br>SFR<br>PWR<br>FNS |

All the TENDL chains are made with `generate_tendl_chain` using decay data and
neutron induced fission yields from ENDF/B-VIII.0, so the releases can be
compared against one another.

FNS (fusion neutron source) adds branching ratios for the production of
metastable states, which makes these chains suitable for activation calculations
of fusion neutron spectra. They are produced with `generate_branching_ratios`
from the isomeric production data in the TENDL files themselves, collapsed with a
spectrum from the [IAEA CoNDERC FNS benchmark](https://nds.iaea.org/conderc/fusion/).

FNS-ORIGEN is an earlier TENDL 2017 and 2019 chain hosted on the
[openmc_activator](https://github.com/jbae11/openmc_activator) repository, whose
branching ratios are derived from ORIGEN data rather than from TENDL. It is kept
available for comparison, but the FNS chains are the TENDL only option and the
two can differ substantially. For Ag107 capture to Ag108_m1 under a fusion
spectrum, for example, FNS gives 0.056 against FNS-ORIGEN's 0.348, because the
FNS value is reaction rate weighted and the majority of the capture rate sits in
the resolved resonance range where the isomeric ratio is small.

<!-- | Sctipt name | Library | Release | Download available | Download ENDF files and generates XML chain files |
|-|-|-|-|-|
|generate_endf71_chain_casl|ENDF/B|-|[https://github.com/openmc-dev/data/tree/master/depletion](https://github.com/openmc-dev/data/tree/master/depletion)|:heavy_check_mark:|
|generate_endf_chain|ENDF/B|-|[https://github.com/openmc-dev/data/tree/master/depletion](https://github.com/openmc-dev/data/tree/master/depletion)|:heavy_check_mark:|
|generate_serpent_fissq|-|-|[https://github.com/openmc-dev/data/tree/master/depletion](https://github.com/openmc-dev/data/tree/master/depletion)|:heavy_check_mark:|
|generate_tendl_chain|TENDL|2019<br>2021|[https://github.com/openmc-dev/data/tree/master/depletion](https://github.com/openmc-dev/data/tree/master/depletion)|:heavy_check_mark:| -->

## Other scripts

| Script name | Description |
|-|-|
| convert_tendl_rand | Download random TENDL libraries from PSI and convert it to a HDF5 library for use with OpenMC. Only certain nuclides are available from PSI. This script generates a cross_sections_tendl.xml file with random TENDL evaluations plus a standard library located in 'OPENMC_CROSS_SECTIONS' |
| sample_sandy | This scripts generates random (gaussian) evaluations of a nuclear data file following its covariance matrix using SANDY, and converts them to HDF5 for use in OpenMC. Script generates a cross_sections_sandy.xml file with the standard library plus the sampled evaluations. |
| make_compton | |
| make_stopping_powers | |
| generate_branching_ratios | Finds the branching ratios for the production of metastable states in the ENDF neutron files and collapses them with a multigroup neutron flux, writing a JSON file for add_branching_ratios. |
| add_branching_ratios | Adds branching ratios to a preexisting chain file, for any reaction present in the JSON file provided. |
| reduce_chain | |
| combine_libraries | Combines multiple cross_section.xml files into a single cross_section.xml. |
