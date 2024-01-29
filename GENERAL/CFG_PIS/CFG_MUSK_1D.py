import os
import pandas as pd
import numpy as np

name='Muskrat winter lodge survival probability'

type='1D'

dct_var={'VAR1':'Freezing probability', 'VAR2':'Relodging probabilty', 'VAR3':'Survival probability'}

#normal mean higher is better
var_direction={'Freezing probability':'inverse','Relodging probabilty': 'normal','Survival probability':'normal'}

units='%'

available_years=list(range(1926, 2017))

available_sections=['LKO_CAN', 'USL_CAN']

sect_dct={'Lake Ontario Canada':['LKO_CAN'], 'Upper St.Lawrence Canada':['USL_CAN'], 'Canada':['LKO_CAN', 'USL_CAN']}
 
mock_map_sct_dct={'LKO_CAN':['LKO'], 'USL_CAN':['SLR_DS', 'SLR_UP', 'USL_DS', 'USL_UP' ]}

available_plans=['Alt_1', 'Alt_2']

plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2'}

available_baselines=['Baseline']

baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline'}

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

