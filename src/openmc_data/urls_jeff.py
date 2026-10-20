"""ENDF inputs for JEFF generation, separate from the processed ACE registry.

NEA record metadata and archive previews were checked on 2026-10-20.
The JEFF 4.0 pairs follow openmc-dev/data's generate_jeff.py (128 pairs).
In particular, ``tsl_O_D20.jeff`` really uses a zero in the archive name.
The additional temperature-split PuO2/UO2/Zy4 evaluations are not mapped by
that upstream generator and are deliberately not included here.
"""


THERMAL_PAIRS_33 = (
    ('1-H-1g.jeff33', 'tsl-HinCaH2.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinCH2.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinH2O.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinIce.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinMesitylene-PhaseII.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinOrthoH.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinParaH.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinToluene.jeff33'),
    ('1-H-1g.jeff33', 'tsl-HinZrH.jeff33'),
    ('1-H-2g.jeff33', 'tsl-DinD2O.jeff33'),
    ('1-H-2g.jeff33', 'tsl-DinOrthoD.jeff33'),
    ('1-H-2g.jeff33', 'tsl-DinParaD.jeff33'),
    ('4-Be-9g.jeff33', 'tsl-Be.jeff33'),
    ('6-C-0g.jeff33', 'tsl-Graphite.jeff33'),
    ('8-O-16g.jeff33', 'tsl-O16inAl2O3.jeff33'),
    ('8-O-16g.jeff33', 'tsl-OinD2O.jeff33'),
    ('12-Mg-24g.jeff33', 'tsl-Mg.jeff33'),
    ('13-Al-27g.jeff33', 'tsl-Al27inAl2O3.jeff33'),
    ('14-Si-28g.jeff33', 'tsl-Silicon.jeff33'),
    ('20-Ca-40g.jeff33', 'tsl-CainCaH2.jeff33'),
)

# Grouped by incident evaluation; material suffixes retain the archive spelling.
_THERMAL_MATERIALS_40 = {
    '1-H-001g': '''H_Benzene H_C5O2H8 H_C8H8 H_CaH2 H_CaO2H2 H_CH2
        H_CH4-liquid H_CH4-solid H_H2O H_HF H_Ice H_KOH H_LiH H_Mesitylene
        H_MgH2 H_MgOH2 H_NaMgH3 H_NaOH H_ortho-H H_para-H H_ParaffinicOil
        H_SrH2 H_Toluene H_UH3 H_YH2 H_ZrH H_ZrH15 H_ZrH2''',
    '1-H-002g': 'D_7LiD D_D2O D_MgD2 D_ortho-D D_para-D',
    '3-Li-007g': '7Li_7LiD Li_FLiBe Li_LiF Li_LiH',
    '4-Be-009g': 'Be_Be Be_Be2C Be_BeF2 Be_BeO Be_FLiBe',
    '6-C-012g': 'C_Be2C C_C5O2H8 C_C8H8 C_CF2 C_CH2 C_Diamond C_Graphite C_UC C_ZrC',
    '7-N-014g': 'N_GaN N_UN',
    '8-O-016g': '''O_Al2O3 O_BeO O_C5O2H8 O_CaO2H2 O_D20 O_Ge3Bi4O12
        O_KOH O_MgO O_MgOH2 O_NaOH O_Y3Al5O12''',
    '9-F-019g': 'F_BeF2 F_CF2 F_FLiBe F_LiF F_MgF2',
    '11-Na-023g': 'Na_Na Na_NaI Na_NaMgH3 Na_NaOH',
    '12-Mg-024g': 'Mg_Mg Mg_MgD2 Mg_MgF2 Mg_MgH2 Mg_MgO Mg_MgOH2 Mg_NaMgH3',
    '13-Al-027g': 'Al_Al Al_Al2O3 Al_Y3Al5O12',
    '14-Si-028g': 'Si_Si',
    '16-S-032g': 'S_ZnS',
    '19-K-039g': 'K_K K_KOH',
    '20-Ca-040g': 'Ca_Ca Ca_CaH2 Ca_CaO2H2',
    '22-Ti-048g': 'Ti_Ti',
    '23-V-051g': 'V_V',
    '24-Cr-052g': 'Cr_Cr',
    '26-Fe-056g': 'Fe_Fe-alpha Fe_Fe-gamma',
    '28-Ni-058g': 'Ni_Ni',
    '29-Cu-063g': 'Cu_Cu',
    '30-Zn-064g': 'Zn_Zn Zn_ZnS',
    '31-Ga-069g': 'Ga_GaN Ga_GaSe',
    '32-Ge-074g': 'Ge_Ge Ge_Ge3Bi4O12 Ge_GeTe',
    '34-Se-080g': 'Se_GaSe',
    '38-Sr-088g': 'Sr_SrH2',
    '39-Y-089g': 'Y_Y3Al5O12 Y_YH2',
    '40-Zr-090g': 'Zr_Zr Zr_ZrC Zr_ZrH15 Zr_ZrH2',
    '41-Nb-093g': 'Nb_Nb',
    '42-Mo-098g': 'Mo_Mo',
    '46-Pd-106g': 'Pd_Pd',
    '47-Ag-107g': 'Ag_Ag',
    '50-Sn-120g': 'Sn_Sn',
    '52-Te-130g': 'Te_GeTe',
    '53-I-127g': 'I_NaI',
    '74-W-184g': 'W_W',
    '78-Pt-195g': 'Pt_Pt',
    '79-Au-197g': 'Au_Au',
    '82-Pb-208g': 'Pb_Pb',
    '83-Bi-209g': 'Bi_Bi Bi_Ge3Bi4O12',
    '92-U-238g': 'U_U U_UC U_UN',
}
THERMAL_PAIRS_40 = tuple(
    (f'n_{neutron}.jeff', f'tsl_{material}.jeff')
    for neutron, materials in _THERMAL_MATERIALS_40.items()
    for material in materials.split()
)


jeff_endf_details = {
    '3.3': {
        'neutron': {
            'base_url': 'https://data.oecd-nea.org/api/records/bh7jn-rm903/files/',
            'compressed_files': ['JEFF33-n.tgz'],
            'url_suffix': '/content',
            'checksums': ['e540bbf95179257280c61acfa75c83de'],
            'pattern': '*.jeff33',
        },
        'thermal': {
            'base_url': 'https://data.oecd-nea.org/api/records/3nm84-46r21/files/',
            'compressed_files': ['JEFF33-tsl.tgz'],
            'url_suffix': '/content',
            'checksums': ['82a6df4cb802aa4a09b95309f7861c54'],
            'pairs': THERMAL_PAIRS_33,
        },
        'photon': {
            'base_url': 'https://www.nndc.bnl.gov/endf-b8.0/zips/',
            'compressed_files': ['ENDF-B-VIII.0_photoat.zip', 'ENDF-B-VIII.0_atomic_relax.zip'],
            'checksums': ['d49f5b54be278862e1ce742ccd94f5c0', 'e04d50098cb2a7e4fe404ec4071611cc'],
        },
    },
    '4.0': {
        'neutron': {
            'base_url': 'https://data.oecd-nea.org/api/records/e9ajn-a3p20/files/',
            'compressed_files': ['JEFF40-Evaluations-Neutron-593.zip'],
            'url_suffix': '/content',
            'checksums': ['51d00ee7bf1491d428f9b30a9782e41d'],
            'pattern': '*.jeff',
        },
        'thermal': {
            'base_url': 'https://data.oecd-nea.org/api/records/scmva-nqh68/files/',
            'compressed_files': ['JEFF40-Evaluations-TSL.zip'],
            'url_suffix': '/content',
            'checksums': ['13d22cd59f83368885ab2d86300b470a'],
            'pairs': THERMAL_PAIRS_40,
        },
        'photon': {
            'base_url': 'https://www.nndc.bnl.gov/endf-releases/releases/B-VIII.1/',
            'compressed_files': ['photoat/photoat-version.VIII.1.tar.gz',
                                 'atomic_relax/atomic_relax-version.VIII.1.tar.gz'],
            'checksums': ['6d5f4830f6290d6c618803a8391ba0cf', '70e9ca0c481236499b7a3e0a490f4ef2'],
        },
    },
}

# Individual IAEA archives avoid downloading the 3 GB official TENDL bulk tar.
# These replace defective JEFF 3.3 MF=6 evaluations, without modifying originals.
# IAEA does not publish checksums here; ZIP CRCs and the ENDF target are checked.
jeff33_replacements = {
    '6-C-13g.jeff33': {
        'base_url': 'https://www-nds.iaea.org/public/download-endf/TENDL-2019/n/',
        'compressed_files': ['n_6-C-13_0628.zip'],
        'checksums': [None],
        'target': (6, 13),
    },
    '8-O-17g.jeff33': {
        'base_url': 'https://www-nds.iaea.org/public/download-endf/TENDL-2019/n/',
        'compressed_files': ['n_8-O-17_0828.zip'],
        'checksums': [None],
        'target': (8, 17),
    },
}