import os

name='Wildfowl'

type='2D_tiled'

dct_var={'VAR1':'Migration habitat', 'VAR2':'Rearing habitat'}
# need to be 'mean' or 'sum', values need to be a list even if there is only one item

var_agg_stat={'VAR1':['sum'],'VAR2':['sum']}

#normal mean higher is better
var_direction={'Migration habitat':'normal', 'Rearing habitat':'normal'}

units='Hectares'

multiplier=0.01

available_years=list(range(1963, 2021))

divided_by_country=False

available_sections = ['SLR_DS', 'SLR_US']

# sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

sect_dct = {'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US'] }

dct_tile_sect = {'SLR_DS': [100, 102, 103, 105, 109, 110, 111, 112, 116, 117, 118, 83, 86, 87, 88, 90, 91, 92, 93, 94, 95, 99, 89, 98, 84],
                 'SLR_US': [121, 126, 127, 128, 133, 134, 141, 142]}

mock_map_sct_dct = {'St.Lawrence River upstream': ['St.Lawrence River upstream'], 'St.Lawrence River downstream': ['St.Lawrence River downstream']}

available_plans=['1958DD', 'Bv7_2014', 'Bv7_GERBL1']

plan_dct={'1958DD':'1958DD', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['PreProjectHistorical']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}
available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'