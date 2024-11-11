import pandas as pd
import os

name='Exposed Riverbed During Winter 2D'

type='2D_tiled'

dct_var={'VAR1':'Total exposed riverbed area during winter'}

#normal mean higher is better (normal or inverse)
var_direction={'Total exposed riverbed area during winter':'inverse'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum']}

multiplier=0.01

units='Hectares'

available_years = list(range(1963, 2021))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_DS', 'SLR_US']


sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS'], 'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US']}

available_plans=['OBS', 'Bv7_2014', 'Bv7_GERBL1']

plan_dct={'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['PreProjectHistorical']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'