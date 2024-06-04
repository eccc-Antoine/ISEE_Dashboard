import os

name='Number of Flooded Residential Buildings(Duration)'

type='2D_not_tiled'

dct_var={'VAR1': 'Primary residential buildings', 'VAR2': 'Secondary residential buildings', 'VAR3': 'All residential buildings' }

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['sum'], 'VAR3':['sum']}

#normal mean higher is better
var_direction={'Primary residential buildings':'inverse', 'Secondary residential buildings':'inverse', 'All residential buildings':'inverse'}

units='QM/Buldings'

multiplier=1

available_years=list(range(1962, 2021))

divided_by_country=True

available_sections=['SLR_DS_CAN']

# available_sections=['LKO']

sect_dct={'St.Lawrence River downstream':['SLR_DS_CAN']}

# sect_dct={'Lake Ontario':['LKO']}

dct_tile_sect={'SLR_DS_CAN': [100, 102, 103, 105, 109, 110, 111, 112, 116, 117, 118, 83, 86, 87, 88, 90, 91, 92, 93, 94, 95,
                          99, 89, 98, 84]}

mock_map_sct_dct={'St.Lawrence River downstream':['St.Lawrence River downstream']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'