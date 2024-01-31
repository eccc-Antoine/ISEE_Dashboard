import numpy

name='Meadow Marsh Area'

type='1D'

dct_var={'VAR1':'Meadow Marsh Area'}

#has to be 'normal' or 'inverse' normal mean higher is better
var_direction={'Meadow Marsh Area':'inverse'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum', 'mean']}

units='ha'

available_years=list(range(1961, 2021))

available_sections=['LKO']

sect_dct={'Lake Ontario':['LKO']}

mock_map_sct_dct={'LKO':['LKO']}

available_plans=['Bv7p620nosepinfop_v20240115']

plan_dct={'Optimized Plan': 'Bv7p620nosepinfop_v20240115'}

available_baselines=['Bv7baseline_v20240115']

baseline_dct={'Baseline': 'Bv7baseline_v20240115'}



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