import os

name='GLRRM'

exp_list=['Bv7_ilimit_flow_692_NG_historical_1900_2008', 'Bv7_ilim_jlim_mods_NG_historical_1900_2008', 'Bv7_no_j_limit_NG_historical_1900_2008', 'Bv7_winter_lstd_level_constraint_71dot7_NG_historical_1900_2008']

exp_meta=fr"F:\DEM_GLAMM\Dashboard\GLRRM\experiments.csv"

loc_list=['ont', 'corn', 'sorl', 'triv']

loc_dct={'ont':'Lake Ontario', 'corn': 'Cornwall', 'sorl': 'Sorel', 'triv':'Trois-Riviere'}

title='PLAN FOMULATION DASHBOARD 0.1.'

raw_data_base=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/inform_optim_db.sqlite'
#raw_data_base=r"F:\DEM_GLAMM\Dashboard\GLRRM\inform_optim_db.sqlite"

#post_process_folder=fr'M:\ISEE_Dashboard\DATA\{name}\{name}_POST_PROCESS_DATA'
post_process_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_POST_PROCESS_DATA'

title=f'{name} DASHBOARD 0.1.'


