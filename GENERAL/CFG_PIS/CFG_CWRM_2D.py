import os

name='Wetland class area'

type='2D'

dct_var={'VAR1':'Open Water', 'VAR2':'Submerged Aquatic Vegetation', 'VAR3':'Emergent Marsh', 'VAR4':'Wet Meadow', 'VAR5':'Swamp', 'VAR6':'Upland', 'VAR7':'Total Wetland Area'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['sum'],'VAR3':['sum'],'VAR4':['sum'],'VAR5':['sum'],'VAR6':['sum'],'VAR7':['sum'],}

#normal mean higher is better
var_direction={'Open Water':'normal', 'Submerged Aquatic Vegetation':'normal', 'Emergent Marsh':'normal', 'Wet Meadow':'normal', 'Swamp':'normal', 'Upland':'normal', 'Total Wetland Area':'normal'}

units='Hectares'

available_years=list(range(1962, 2021))

available_sections=['LKO', 'USL_US', 'USL_DS']

# available_sections=['LKO']

sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

# sect_dct={'Lake Ontario':['LKO']}

dct_tile_sect={'USL_US':[181,184,183,186,191,187,
 197,198,205,206,216,217,226],
 'LKO':[202, 209, 212, 213, 215, 219, 222, 225, 236, 237, 248, 249, 251, 261, 262, 273,
 283, 284, 285, 292, 293, 294, 295, 296, 306, 307, 318, 319, 330, 331, 334, 343, 344,
 346, 354, 357, 365, 366, 413, 420, 430, 447, 457, 459, 466, 483, 487, 489, 490, 491],
 'USL_DS':[167,169,170,171,172,174,175,178,181,182]}

 
mock_map_sct_dct={'Lake Ontario':['Lake Ontario'], 'Upper St.Lawrence upstream':['Upper St.Lawrence upstream'], 'Lake St.Lawrence':['Lake St.Lawrence']}

available_plans=['Bv7_2014']

plan_dct={'Bv7_2014': 'Bv7_2014'}

available_baselines=['Bv7']

baseline_dct={'Bv7': 'Bv7'}

available_stats=['sum', 'mean']

id_column_name='PT_ID'