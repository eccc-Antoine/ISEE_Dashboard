import os

name='ISEE'

pi_list=['ESLU_2D', 'RES_BUILD_2D', 'MUSK_1D', 'EX_RB_1D', 'NAVC_1D']

#===============================================================================
# sect_dct={'Lake Ontario Canada':['LKO_CAN'], 'Upper St.Lawrence Canada':['USL_CAN'], 'Canada':['LKO_CAN', 'USL_CAN'], 'Lake St.Lawrence':['USL_DS'], 'Upper St. Lawrence': ['USL']}
#  
# mock_map_sct_dct={'LKO_CAN':['LKO'], 'USL_CAN':['SLR_DS', 'SLR_UP', 'USL_DS', 'USL_UP' ], 'USL_DS':['USL_DS'], 'USL':['USL_DS', 'USL_UP']}
#  
# baselines=['actual plan', 'pristine state']
#  
# baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline'}
#  
# baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline'}
#  
# plans=[]
# for i in range(1,3):
#     plan=f'Plan {str(i)}'
#     plans.append(plan)
#  
# plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2'}
# 
# 
# #===============================================================================
# # pi_list=['WLVL_1D', 'NAVC_1D']
# #===============================================================================
# 
# sect_dct={'Lake_ontario': ['LKO'], 
#           'Upper St.lawrence upstream':['USL_UP'],
#           'Upper St.lawrence downstream':['USL_DN'],
#           'Upper St.lawrence':['USL'],
#           'Lower St. Lawrence upstream':['SLR_UP'],
#           'Lower St.Lawrence downstream':['SLR_DN']}
#  
# baselines=['baseline Plan 2014 without deviations']
#  
# baseline_dct={'baseline Plan 2014 without deviations':'Bv7_baseline_NG_historical'}
#  
# plans=['Bv7_policy_1025_Flim_skipT1_add3T_NG_historical_1900_2020', 'Bv7_policy_1025_NG_historical_1900_2020']
#  
# plan_dct={'Optimized 2014 Plan': 'Bv7_policy_1025_NG_historical_1900_2020',
#         'Optimized 2014 Plan w. modified F limit': 'Bv7_policy_1025_Flim_skipT1_add3T_NG_historical_1900_2020'}
#===============================================================================


title=f'{name} DASHBOARD 0.5.'

raw_data_folder=fr'M:\DATA\{name}\{name}_RAW_DATA'
#raw_data_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/DATA/{name}/{name}_RAW_DATA'

post_process_folder=fr'M:\DATA\{name}\{name}_POST_PROCESS_DATA'
#post_process_folder=f'https://raw.githubusercontent.com/eccc-Antoine/ISEE_Dashboard/main/{name}_POST_PROCESS_DATA'

file_ext='.feather'

sct_poly=os.path.join(raw_data_folder, "SECTIONS.geojson")

maximum_plan_to_compare=2

crs=2618

