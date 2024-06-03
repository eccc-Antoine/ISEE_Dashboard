import os

name='Marsh Birds'

type='2D_not_tiled'

dct_var={'VAR1': 'Abundance', 'VAR2': 'Richness'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['mean']}

#normal mean higher is better
var_direction={'Abundance':'normal', 'Richness':'normal'}

units=' '

multiplier=1

available_years=list(range(1995, 2021))

divided_by_country=False

available_sections=['LKO']

# available_sections=['LKO']

sect_dct={'Lake Ontario':['LKO']}

# sect_dct={'Lake Ontario':['LKO']}

dct_tile_sect={
 'LKO':[202, 209, 212, 213, 215, 219, 222, 225, 236, 237, 248, 249, 251, 261, 262, 273,
 283, 284, 285, 292, 293, 294, 295, 296, 306, 307, 318, 319, 330, 331, 334, 343, 344,
 346, 354, 357, 365, 366, 413, 420, 430, 447, 457, 459, 466, 483, 487, 489, 490, 491],}

 
mock_map_sct_dct={'Lake Ontario':['Lake Ontario']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'