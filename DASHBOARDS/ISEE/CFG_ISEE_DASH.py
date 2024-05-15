import os

name='ISEE'

#pi_list=['ESLU_2D', 'RES_BUILD_2D', 'MUSK_1D', 'EX_RB_1D', 'NAVC_1D', 'ONZI_1D']

pi_list=['ONZI_1D', 'NAVC_1D', 'MM_1D',  'EX_RB_1D', 'BUILD_2D', 'TURTLE_1D', 'ZIPA_1D']


title=f'{name} DASHBOARD 0.5.'

raw_data_folder=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA'
#raw_data_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_RAW_DATA'

post_process_folder=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA'
#post_process_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/{name}_POST_PROCESS_DATA'

file_ext='.feather'

sct_poly="H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\SECTIONS_simple_US_DS_longnames.geojson"

maximum_plan_to_compare=2

crs=2618

