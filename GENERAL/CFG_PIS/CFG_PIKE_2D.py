import pandas as pd
import os

name='Northern Pike habitat'

type='2D_tiled'

dct_var={'VAR1': 'Habitat available for spawning and embryo-larval development'}

#normal mean higher is better (normal or inverse)
var_direction={'Habitat available for spawning and embryo-larval development':'normal'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum']}

units='Hectares'

multiplier=1

available_years = list(range(1963, 2021))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_DS', 'SLR_US']

sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS'], 'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'