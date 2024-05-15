import numpy

name='Wild rice'

type='1D'

dct_var={'VAR1':'Survival probability'}

#'normal' means higher is better
var_direction={'Survival probability':'normal'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean']}

units='%'

available_years=list(range(1980, 2019))

available_sections=['LKO', 'USL_US', 'USL_DS']

sect_dct={'Lake Ontario':['LKO'],
           'Upper St.Lawrence upstream':['USL_US'],
            'Lake St.Lawrence':['USL_DS']}


mock_map_sct_dct={'LKO':['LKO'], 'USL_US':['USL_US'], 'USL_DS':['USL_DS']}

available_plans=['Bv7_2014', 'Bv7_GERBL1']

plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['Bv7']

baseline_dct={'Bv7': 'Bv7'}

available_stats=['mean']
