import numpy

name='Muskrat winter lodge viability'

type='1D'

dct_var={'VAR1':'Probability of Lodge Viability'}

#normal mean higher is better
var_direction={'Probability of Lodge Viability':'normal'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean']}

units='%'

multiplier=1

available_years=list(range(1962, 2018))

divided_by_country=False

#available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']
#available_sections=['LKO', 'USL_US', 'SLR_US', 'SLR_DS']
available_sections=['LKO', 'USL_US', 'SLR_US']



sect_dct={'Lake Ontario':['LKO'],
           'Upper St.Lawrence upstream':['USL_US'],
              'St.Lawrence River upstream':['SLR_US'],
               'St.Lawrence River downstream':['SLR_DS'],
               'Upstream':['LKO', 'USL_US'],
               'Downstream':['USL_DS', 'SLR_US', 'SLR_DS']}

# sect_dct={'Lake Ontario':['LKO'],
#            'Upper St.Lawrence upstream':['USL_US'],
#             'Lake St.Lawrence':['USL_DS'],
#               'St.Lawrence River upstream':['SLR_US'],
#                'St.Lawrence River downstream':['SLR_DS'],
#                'Upstream':['LKO', 'USL_US'],
#                'Downstream':['USL_DS', 'SLR_US', 'SLR_DS']}



#mock_map_sct_dct={'LKO':['LKO'], 'USL_US':['USL_US'], 'USL_DS':['USL_DS'], 'SLR_US':['SLR_US'], 'SLR_DS':['SLR_DS'], 'USL':['USL'], 'SLR':['SLR']}
mock_map_sct_dct={'LKO':['LKO'], 'USL_US':['USL_US'], 'SLR_US':['SLR_US'], 'SLR_DS':['SLR_DS'], 'USL':['USL'], 'SLR':['SLR']}


available_plans=['Bv7_2014', 'Bv7', 'OBS', 'PRE_PROJ']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS', 'Pre Project': 'PRE_PROJ'}

available_baselines=['Bv7_GERBL1']

baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'

