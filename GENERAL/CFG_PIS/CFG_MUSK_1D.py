import os
import pandas as pd
import numpy as np

name='Muskrat winter lodge survival probability'

type='1D'

dct_var={'VAR1':'Freezing probability', 'VAR2':'Relodging probabilty', 'VAR3':'Survival probability'}

units='%'

available_years=list(range(1926, 2017))

available_sections=['LKO_CAN', 'USL_CAN']

available_plans=['Alt_1', 'Alt_2']

available_baselines=['Baseline']

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

