import pandas as pd
import os

name = 'Marsh Birds'

type = '2D'

dct_var = {'VAR1': 'Number of nesting couples'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat = {'VAR1': ['sum']}

# normal mean higher is better
var_direction = {'Nb': 'normal'}

units = 'Number of nests'

available_years = list(range(1963, 2021))

# available_sections=['LKO', 'USL_US', 'USL_DS']

available_sections = ['SLR_DS', 'SLR_US']

# sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

sect_dct = {'St. Lawrence River downstream': ['SLR_DS'], 'St. Lawrence River upstream': ['SLR_US'] }

dct_tile_sect = {'SLR_DS': [100, 102, 103, 105, 109, 110, 111, 112, 116, 117, 118, 83, 86, 87, 88, 90, 91, 92, 93, 94, 95, 99, 89, 98, 84],
                 'SLR_US': [121, 126, 127, 128, 133, 134, 141, 142]}

mock_map_sct_dct = {'SLR_DS': ['SLR_DS']}

available_plans=['Bv7_2014', 'Bv7_GERBL1', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7_GERBL1':'Bv7_GERBL1', 'Observation':'OBS'}

available_baselines=['Bv7']

baseline_dct={'Bv7': 'Bv7'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'