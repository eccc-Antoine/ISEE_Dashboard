import os
import pandas as pd
import numpy as np

name='Exposed River Bed'

type='2D_tiled'

dct_var={'VAR1':'Exposed QM during ice in period'}

var_agg_stat={'VAR1':['mean']}

#normal mean higher is better
var_direction={'Exposed QM during ice in period':'inverse'}

units='QM'

available_years=list(range(1981, 2020))

available_sections=['USL_DS']

sect_dct={'Lake St.Lawrence':['USL_DS']}

mock_map_sct_dct={'USL_DS':['USL_DS']}

available_plans=['Bv7p620nosepinfop_v20240115']

plan_dct={'Optimized PLan': 'Bv7p620nosepinfop_v20240115'}

available_baselines=['Bv7baseline_v20240115']

baseline_dct={'Baseline': 'Bv7baseline_v20240115'}

available_stats=['mean', 'sum']

dct_tile_sect={'USL_DS':[169, 170, 172, 173, 174, 175, 176, 178, 179, 181, 182]}

id_column_name='PT_ID'

## Mock equation just to implement the routine
locs_for_GLRRM=['alex']
def GLRRM_1D_equations (df):
    d = {'year': df['year'].unique(), 'PI_1D_value': np.nan}
    df_y = pd.DataFrame(data=d)
    for y in df['year'].unique():
        value1=df['values_max'].loc[(df['location']=='alex') & (df['kind']=='mlv') & (df['year']==y)].iloc[0]
        value2=df['values_min'].loc[(df['location']=='alex') & (df['kind']=='mlv') & (df['year']==y)].iloc[0]
        eq=((value1-value2)*0.42)+120
        df_y['PI_1D_value'].loc[df_y['year']==y]=eq
    return df_y

