import os

name='Least Bittern'

type='2D_tiled'

dct_var={'VAR1': 'Weighted usable area', 'VAR2': 'Sub-Optimal WUA', 'VAR3': 'Optimal WUA'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['sum'],'VAR3':['sum']}

#normal mean higher is better
var_direction={'RPI_IXEX':'normal', 'RPI_sub-optimal_IXEX':'normal', 'RPI_optimal_IXEX':'normal'}

units='Hectares'

multiplier=0.01

available_years=list(range(1963, 2021))

divided_by_country=False

available_sections = ['SLR_DS', 'SLR_US']

# sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

sect_dct = {'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US'] }

available_plans=['1958DD', 'Bv7_2014', 'Bv7_GERBL1']

plan_dct={'1958DD':'1958DD', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['PreProjectHistorical']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'