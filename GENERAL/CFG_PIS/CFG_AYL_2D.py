import os

name = 'Agriculture Yield Loss'

type = '2D_not_tiled'

dct_var = {'VAR1': 'Average Yield Loss for all crops'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat = {'VAR1': ['sum']}

# normal mean higher is better
var_direction = {'Average Yield Loss for all crops': 'inverse'}

units = '$'

multiplier = 1

available_years = list(range(1962, 2021))

divided_by_country = False

available_sections = ['SLR_DS', 'SLR_US']

sect_dct = {'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US'] }

available_plans = ['OBS', 'Bv7_GERBL1']

plan_dct = {'OBS':'OBS', 'Bv7_GERBL1': 'Bv7_GERBL1'}

available_baselines = ['PreProjectHistorical']

baseline_dct = {'PreProjectHistorical': 'PreProjectHistorical'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'