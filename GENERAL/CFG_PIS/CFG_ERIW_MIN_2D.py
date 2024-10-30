import pandas as pd
import os

name='Exposed Riverbed During Winter 2D'

type='2D_tiled'

dct_var={'VAR1':'Total exposed winter area'}

#normal mean higher is better (normal or inverse)
var_direction={'Percent of time exposed during winter':'inverse'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum']}

multiplier=0.01

units='Hectares'

available_years = list(range(1963, 2021))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_DS', 'SLR_US']


sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS'], 'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US']}

dct_tile_sect={'USL_US':[181,184,183,186,191,187,
 197,198,205,206,216,217,226],
 'LKO':[202, 209, 212, 213, 215, 219, 222, 225, 236, 237, 248, 249, 251, 261, 262, 273,
 283, 284, 285, 292, 293, 294, 295, 296, 306, 307, 318, 319, 330, 331, 334, 343, 344,
 346, 354, 357, 365, 366, 413, 420, 430, 447, 457, 459, 466, 483, 487, 489, 490, 491],
 'USL_DS':[167,169,170,171,172,174,175,178,181,182],
'SLR_DS': [100, 102, 103, 105, 109, 110, 111, 112, 116, 117, 118, 83, 86, 87, 88, 90, 91, 92, 93, 94, 95,
                          99, 89, 98, 84],
'SLR_US': [121, 126, 127, 128, 133, 134, 141, 142]
               }

mock_map_sct_dct={'Lake Ontario':['Lake Ontario'], 'Upper St.Lawrence upstream':['Upper St.Lawrence upstream'], 'Lake St.Lawrence':['Lake St.Lawrence'], 'St.Lawrence River upstream': ['St.Lawrence River upstream'], 'St.Lawrence River downstream': ['St.Lawrence River downstream'] }

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'