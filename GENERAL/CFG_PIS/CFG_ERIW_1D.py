import numpy

name='Exposed Riverbed During Winter Index'

type='1D'

dct_var={'VAR1':'Exposed Riverbed During Winter Index'}

#normal mean higher is better (normal or inverse)
var_direction={'Exposed Riverbed During Winter Index':'normal'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean']}

units=' '

multiplier=1

available_years=list(range(1963, 2021))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']


sect_dct={'Lake Ontario':['LKO'],
           'Upper St.Lawrence upstream':['USL_US'],
            'Lake St.Lawrence':['USL_DS'],
              'St.Lawrence River upstream':['SLR_US'],
               'St.Lawrence River downstream':['SLR_DS'],
               'Upstream':['LKO', 'USL_US'],
               'Downstream':['USL_DS', 'SLR_US', 'SLR_DS']}


# sect_dct={'Upstream':['LKO', 'USL_US'],
#            'Downstream':['USL_DS', 'SLR_US', 'SLR_DS']}


mock_map_sct_dct={'LKO':['LKO'], 'USL_US':['USL_US'], 'USL_DS':['USL_DS'], 'SLR_US':['SLR_US'], 'SLR_DS':['SLR_DS'], 'USL':['USL'], 'SLR':['SLR']}

#mock_map_sct_dct={'Upstream':['Lake Ontario', 'Upper St.Lawrence upstream'], 'Downstream':['Lake St.Lawrence', 'St.Lawrence River upstream', 'St.Lawrence River downstream']}

available_plans=['Bv7_2014', 'Bv7', 'OBS']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'
