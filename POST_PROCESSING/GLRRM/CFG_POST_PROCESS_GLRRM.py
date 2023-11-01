import os

name='GLRRM'

rewrite_exp=False

scripts_folder=r"M:\ISEE_Dashboard"

#GLRRM_RES=fr'M:\ISEE_Dashboard\ISEE_RAW_DATA'
GLRRM_RES=r"F:\DEM_GLAMM\Dashboard\GLRRM\inform_optim_db.sqlite"

post_process_folder=fr'M:\ISEE_Dashboard\DATA\{name}\{name}_POST_PROCESS_DATA'
#post_process_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_POST_PROCESS_DATA'

exp_table_name='experiments'
output_table_name='outputs'


exp_col_name='experiment'
location_col_name='location'
year_col_name='year'


sep=';'