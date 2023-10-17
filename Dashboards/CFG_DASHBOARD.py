import os

sect_dct={'Lake Ontario Canada':['LKO_CAN'], 'Upper St.Lawrence Canada':['USL_CAN'], 'Canada':['LKO_CAN', 'USL_CAN'] }

baselines=['actual plan', 'pristine state']

baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline_2'}

plans=[]
for i in range(1,3):
    plan=f'Plan {str(i)}'
    plans.append(plan)

plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2'}

title='ISEE DASHBOARD 0.2.'

#post_process_folder=r'M:\ISEE_Dashboard\ISEE_POST_PROCESS_DATA'
post_process_folder='https://raw.githubusercontent.com/eccc-Antoine/GLAM_DASHBOARD_DEV/main/ISEE_POST_PROCESS_DATA'

maximum_plan_to_compare=2

