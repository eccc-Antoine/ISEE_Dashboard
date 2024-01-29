import os

name='Northern Pike Early Stage development'

type='2D_tiled'

dct_var={'VAR1':'Habitat suitability index', 'VAR2':'Potential mortality index', 'VAR3':'Early stage survival probability'}

#normal mean higher is better
var_direction={'Habitat suitability index':'normal','Potential mortality index': 'inverse','Early stage survival probability':'normal'}

units='ha'

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
