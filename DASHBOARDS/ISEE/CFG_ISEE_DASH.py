import os

name='ISEE'

pi_list=['ESLU_2D', 'RES_BUILD_2D', 'MUSK_1D']

sect_dct={'Lake Ontario Canada':['LKO_CAN'], 'Upper St.Lawrence Canada':['USL_CAN'], 'Canada':['LKO_CAN', 'USL_CAN'] }

baselines=['actual plan', 'pristine state']

baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline_2'}

plans=[]
for i in range(1,3):
    plan=f'Plan {str(i)}'
    plans.append(plan)

plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2'}

title=f'{name} DASHBOARD 0.4.'

#raw_data_folder=fr'M:\ISEE_Dashboard\DATA\{name}\{name}_RAW_DATA'
raw_data_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_RAW_DATA'

#post_process_folder=fr'M:\ISEE_Dashboard\DATA\{name}\{name}_POST_PROCESS_DATA'
post_process_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_POST_PROCESS_DATA'

maximum_plan_to_compare=2

crs=2618

