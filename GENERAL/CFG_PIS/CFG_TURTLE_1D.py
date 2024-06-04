import numpy

name='Turtle survival during winter'

type='1D'

dct_var={'VAR1':'Blanding turtle', 'VAR2':'Snapping turtle', 'VAR3':'Painted turtle' }

#'normal' means higher is better
var_direction={'Blanding turtle':'normal', 'Snapping turtle':'normal', 'Painted turtle':'normal'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean'], 'VAR2':['mean'], 'VAR3':['mean']}

units='%'

multiplier=1

available_years=list(range(1962, 2021))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']


sect_dct={'Lake Ontario':['LKO'],
           'Upper St.Lawrence upstream':['USL_US'],
            'Lake St.Lawrence':['USL_DS'],
              'St.Lawrence River upstream':['SLR_US'],
               'St.Lawrence River downstream':['SLR_DS'],
               'Upstream':['LKO', 'USL_US'],
               'Downstream':['USL_DS', 'SLR_US', 'SLR_DS']}

mock_map_sct_dct={'LKO':['LKO'], 'USL_US':['USL_US'], 'USL_DS':['USL_DS'], 'SLR_US':['SLR_US'], 'SLR_DS':['SLR_DS'], 'USL':['USL'], 'SLR':['SLR']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'


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