import numpy

name='Meadow Marsh Area'

type='1D'

dct_var={'VAR1':'Meadow Marsh Area'}

#has to be 'normal' or 'inverse' normal mean higher is better
var_direction={'Meadow Marsh Area':'normal'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum', 'mean']}

units='Hectares'

multiplier=1

available_years=list(range(1961, 2021))

divided_by_country=False

available_sections=['LKO']

sect_dct={'Lake Ontario':['LKO']}

mock_map_sct_dct={'LKO':['LKO']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'
