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

available_years=list(range(1962, 2021))

divided_by_country=False

available_sections=['LKO']

sect_dct={'Lake Ontario':['LKO']}

available_plans=['1958DD', 'Bv7_2014', 'Bv7_GERBL1']

plan_dct={'1958DD':'1958DD', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['PreProjectHistorical']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'