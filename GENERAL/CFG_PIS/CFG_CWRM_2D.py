import os

name='Wetland class area'

type='2D_tiled'

dct_var={'VAR1':'Open Water', 'VAR2':'Submerged Aquatic Vegetation', 'VAR3':'Emergent Marsh', 'VAR4':'Wet Meadow', 'VAR5':'Swamp', 'VAR6':'Upland', 'VAR7':'Total Wetland Area'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['sum'],'VAR3':['sum'],'VAR4':['sum'],'VAR5':['sum'],'VAR6':['sum'],'VAR7':['sum'],}

#normal mean higher is better
var_direction={'Open Water':'normal', 'Submerged Aquatic Vegetation':'normal', 'Emergent Marsh':'normal', 'Wet Meadow':'normal', 'Swamp':'normal', 'Upland':'normal', 'Total Wetland Area':'normal'}

units='Hectares'

multiplier=0.01

available_years=list(range(1962, 2021))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS']

sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

available_plans=['1958DD', 'Bv7_2014', 'Bv7_GERBL1']

plan_dct={'1958DD':'1958DD', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['PreProjectHistorical']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'
