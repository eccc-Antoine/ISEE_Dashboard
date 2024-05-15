import os

name='Flooded Buildings'

type='1D'

dct_var={'VAR1':'Nb'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum']}

#normal mean higher is better
var_direction={'Nb':'inverse'}

units=''

available_years=list(range(1980, 2020))

#available_sections=['LKO', 'USL_US', 'USL_DS']

available_sections=['LKO']

#sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

sect_dct={'Lake Ontario':['LKO']}

dct_tile_sect={'USL_US':[181,184,183,186,191,187,
 197,198,205,206,216,217,226],'LKO':[226,202,214,203,209,210,211,212,213,
 214,215,219,230,222,223,224,225,229,235,
 236,240,251,252,262,273,274,285,
 297,309,321,334,345,346,357,366,
 375,383,391,392,400,407,414,422,
 430,441,439,440,450,451], 'USL_DS':[167,169,170,171,172,174,175,178,181,182]}

 
mock_map_sct_dct={'Lake Ontario':['Lake Ontario']}

available_plans=['Bv7p620nosepinfop_v20240115']

plan_dct={'Optimized Plan': 'Bv7p620nosepinfop_v20240115'}

available_baselines=['Bv7baseline_v20240115']

baseline_dct={'Baseline': 'Bv7baseline_v20240115'}

available_stats=['sum', 'mean']

id_column_name='PT_ID'