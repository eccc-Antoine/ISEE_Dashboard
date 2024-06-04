import os

name='ISEE'

pis_2D_tiled=['IERM_2D']

#pis_2D_tiled=['IERM_2D', "IXEX_2D"]

#pis_2D_tiled=['PIKE_2D']

pis_2D_not_tiled=['BIRDS_2D']
#pis_2D_not_tiled=['NFB_2D', 'NFBD_2D']


#pis_1D=['MUSK_1D', 'EX_RB_1D']

#pis_1D=['EX_RB_1D']

#pis_1D=['NAVC_1D', 'EX_RB_1D', 'MUSK_1D', 'ONZI_1D']

pis_1D=['ZIPA_1D', 'TURTLE_1D', 'ONZI_1D', 'MM_1D', 'ERIW_1D']

#plans=['Bv7_baseline_NG_historical', 'Bv7_infop_policy_620_nosepRule']

#plans=['Alt_1', 'Alt_2', 'Baseline']

#sections=['USL_CAN', 'LKO_CAN', 'USL_DS']

#sections=['USL']

#years=list(range(1961, 2021))

ISEE_RES=fr'C:\GLAM\Dashboard\ISEE_RAW_DATA'
#ISEE_RES=fr'F:\GLAM_DASHBOARD\ISEE_RAW_DATA'
#ISEE_RES=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA'
#ISEE_RES=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_RAW_DATA'

#POST_PROCESS_RES=fr'F:\GLAM_DASHBOARD\ISEE_POST_PROCESS_DATA'
POST_PROCESS_RES=fr'C:\GLAM\Dashboard\ISEE_POST_PROCESS_DATA'
#POST_PROCESS_RES=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA'
#POST_PROCESS_RES=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_POST_PROCESS_DATA'

sep=';'

#dct_sect={'LKO_CAN':list(range(40, 46)), 'USL_CAN':list(range(45, 47))}

#id_column_name='PT_ID'