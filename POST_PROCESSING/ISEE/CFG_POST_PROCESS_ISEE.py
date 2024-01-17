import os

name='ISEE'

pis_2D_tiled=['ESLU_2D']

pis_2D_not_tiled=['RES_BUILD_2D']

pis_1D=['MUSK_1D']

plans=['Alt_1', 'Alt_2', 'Baseline']

sections=['USL_CAN', 'LKO_CAN']

years=list(range(1926, 2017))

ISEE_RES=fr'M:\DATA\{name}\{name}_RAW_DATA'
#ISEE_RES=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_RAW_DATA'

POST_PROCESS_RES=fr'M:\DATA\{name}\{name}_POST_PROCESS_DATA'
#POST_PROCESS_RES=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_POST_PROCESS_DATA'

sep=';'

dct_sect={'LKO_CAN':list(range(40, 46)), 'USL_CAN':list(range(45, 47))}

id_column_name='PT_ID'