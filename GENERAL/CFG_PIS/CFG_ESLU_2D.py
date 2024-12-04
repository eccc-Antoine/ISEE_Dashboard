import os

name='Northern Pike Early Stage development'

type='2D_tiled'

dct_var={'VAR1':'Weighted sum area of Habitat suitability index', 'VAR2':'Weighted sum area of Potential mortality index', 'VAR3':'Weighted sum area of Early stage survival probability'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean', 'sum'], 'VAR2':['mean', 'sum'], 'VAR3':['mean', 'sum'] }

#normal mean higher is better
var_direction={'Habitat suitability index':'normal', 'Potential mortality index': 'inverse', 'Early stage survival probability':'normal'}

units='ha'

available_years=list(range(1926, 2017))

available_sections=['LKO_CAN', 'USL_CAN']

sect_dct={'Lake Ontario Canada':['LKO_CAN'], 'Upper St.Lawrence Canada':['USL_CAN'], 'Canada':['LKO_CAN', 'USL_CAN']}

available_plans=['Alt_1', 'Alt_2']

plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2'}

available_baselines=['Baseline']

baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline'}

available_stats=['sum', 'mean']

id_column_name='PT_ID'
