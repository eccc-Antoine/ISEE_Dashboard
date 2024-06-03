import os

name='Residential Buildings'

type='2D_not_tiled'

dct_var={'VAR1': 'Number of flooded buildings', 'VAR2': 'Week/buildings flood magnitude'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['sum']}

#normal mean higher is better
var_direction={'Number of flooded buildings':'inverse', 'Week/buildings flood magnitude':'inverse'}

units=' '

multiplier=1

available_years=list(range(1962, 2021))

divided_by_country=True

available_sections=['SLR_DS_CAN', 'SLR_US_CAN', 'LKO_CAN', 'USL_DS_CAN', 'USL_US_CAN', 'LKO_US',
 'USL_US_US', 'USL_DS_US']

sect_dct={'St.Lawrence River downstream Canada':['SLR_DS_CAN'],
          'St.Lawrence River upstream Canada':['SLR_DS_CAN'],
          'Lake Ontario Canada':['LKO_CAN'],
          'Lake St.Lawrence Canada': ['USL_DS_CAN'],
          'Upper St.Lawrence upstream Canada':['USL_US_CAN'],
          'Lake Ontario United States': ['LKO_US'],
          'Upper St.Lawrence upstream United States':['USL_US_US'],
          'Lake St.Lawrence United States':['USL_DS_US']
          }

# sect_dct={'Lake Ontario':['LKO']}

# dct_tile_sect={'SLR_DS_CAN': [100, 102, 103, 105, 109, 110, 111, 112, 116, 117, 118, 83, 86, 87, 88, 90, 91, 92, 93, 94, 95,
#                           99, 89, 98, 84]}

#mock_map_sct_dct={'St.Lawrence River downstream Canada':['St.Lawrence River downstream Canada']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'