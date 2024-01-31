import numpy

name='Muskrat winter lodge viability'

type='1D'

dct_var={'VAR1':'Probability of Lodge Viability'}

#normal mean higher is better
var_direction={'Probability of Lodge Viability':'normal'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum']}

units='%'

available_years=list(range(1981, 2017))

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']

sect_dct={'Lake Ontario':['LKO'],
           'Upper St.Lawrence upstream':['USL_US'],
            'Lake St.Lawrence':['USL_DS'],
             'Upper St.Lawrence':['USL_US', 'USL_DS'],
              'St.Lawrence River upstream':['SLR_US'],
               'St.Lawrence River downstream':['SLR_DS'],
                'St.Lawrence River':['SLR_US', 'SLR_DS' ],
                 'Total':['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']}


mock_map_sct_dct={'LKO':['LKO'], 'USL_US':['USL_US'], 'USL_DS':['USL_DS'], 'SLR_US':['SLR_US'], 'SLR_DS':['SLR_DS'], 'USL':['USL'], 'SLR':['SLR']}

available_plans=['Bv7p620nosepinfop_v20240115']

plan_dct={'Optimized Plan': 'Bv7p620nosepinfop_v20240115'}

available_baselines=['Bv7baseline_v20240115']

baseline_dct={'Baseline': 'Bv7baseline_v20240115'}

available_stats=['mean']


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