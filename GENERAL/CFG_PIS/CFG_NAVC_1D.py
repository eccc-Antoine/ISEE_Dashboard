import os
import pandas as pd
import numpy as np

name='Commercial navigation'

type='1D'

dct_var={'VAR1':'no risk','VAR2':'Warning','VAR3':'Accelerated Risk','VAR4':'High Risk'}

var_agg_stat={'VAR1':['mean'], 'VAR2':['mean'], 'VAR3':['mean'],'VAR4':['mean']}

#normal mean higher is better
var_direction={'no risk':'normal','Warning': 'inverse','Accelerated Risk':'inverse', 'High Risk':'inverse'}

units='Number of QM'

available_years=list(range(1961, 2021))

available_sections=['USL']

sect_dct={'Upper St.lawrence':['USL']}

mock_map_sct_dct={'USL':['USL_DS', 'USL_US']}

available_plans=['Bv7_infop_policy_620_nosepRule']
plan_dct={'Optimized Plan': 'Bv7_infop_policy_620_nosepRule'}

available_baselines=['Bv7_baseline_NG_historical']
baseline_dct={'baseline Plan 2014 without deviations':'Bv7_baseline_NG_historical'}

available_stats=['sum', 'mean']


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

