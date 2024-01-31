import os

name='Residential building damage'

type='2D_not_tiled'

dct_var={'VAR1':'Structural damages', 'VAR2':'Material damages', 'VAR3':'Total damage'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean', 'sum'], 'VAR2':['mean', 'sum'], 'VAR3':['mean', 'sum'] }

#normal mean higher is better
var_direction={'Structural damages':'inverse','Material damages': 'inverse','Total damage':'inverse'}

units='K$ CAN'

available_years=list(range(1926, 2017))

available_sections=['LKO_CAN', 'USL_CAN']

sect_dct={'Lake Ontario Canada':['LKO_CAN'], 'Upper St.Lawrence Canada':['USL_CAN'], 'Canada':['LKO_CAN', 'USL_CAN']}

dct_tile_sect={'LKO_CAN':list(range(40, 46)), 'USL_CAN':list(range(45, 47))}
 
mock_map_sct_dct={'LKO_CAN':['LKO'], 'USL_CAN':['SLR_DS', 'SLR_UP', 'USL_DS', 'USL_UP' ]}

available_plans=['Alt_1', 'Alt_2']

plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2'}

available_baselines=['Baseline']

baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline'}

available_stats=['sum', 'mean']

id_column_name='PT_ID'