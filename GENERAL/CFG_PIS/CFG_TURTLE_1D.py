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

available_years_hist=list(range(1962, 2021))
available_years_future=list(range(2011, 2071))
divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']


sect_dct={'Lake Ontario':['LKO'],
           'Upper St.Lawrence upstream':['USL_US'],
            'Lake St.Lawrence':['USL_DS'],
              'St.Lawrence River upstream':['SLR_US'],
               'St.Lawrence River downstream':['SLR_DS'],
               'Upstream':['LKO', 'USL_US'],
               'Downstream':['USL_DS', 'SLR_US', 'SLR_DS']}

#
# available_plans=['OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014BOC_comboD', 'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboC_STO_330_GLRRM', 'GERBL2_2014_STO_330_GLRRM', 'GERBL2_2014_ComboC_RCP45_GLRRM', 'GERBL2_2014BOC_RCP45_GLRRM', 'Bv7_2014_ComboC_GLRRM',  'Bv7_2014_GLRRM']
#
# plans_ts_dct={'hist':['OBS', 'Bv7_2014', 'Bv7_2014_ComboC','GERBL2_2014BOC_comboD', 'Bv7_2014_ComboC_GLRRM',  'Bv7_2014_GLRRM'], 'sto':['GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboC_STO_330_GLRRM', 'GERBL2_2014_STO_330_GLRRM'], 'cc':['GERBL2_2014BOC_RCP45','GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboC_RCP45_GLRRM', 'GERBL2_2014BOC_RCP45_GLRRM']}
#
# plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC','GERBL2_2014BOC_comboD', 'Bv7_2014_ComboC_GLRRM',  'Bv7_2014_GLRRM']
#
# plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330':'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014BOC_comboD': 'GERBL2_2014BOC_comboD', 'GERBL2_2014_ComboD_STO_330':'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboD_RCP45':'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboC_STO_330_GLRRM':'GERBL2_2014_ComboC_STO_330_GLRRM', 'GERBL2_2014_STO_330_GLRRM': 'GERBL2_2014_STO_330_GLRRM', 'GERBL2_2014_ComboC_RCP45_GLRRM':'GERBL2_2014_ComboC_RCP45_GLRRM', 'GERBL2_2014BOC_RCP45_GLRRM':'GERBL2_2014BOC_RCP45_GLRRM', 'Bv7_2014_ComboC_GLRRM':'Bv7_2014_ComboC_GLRRM',  'Bv7_2014_GLRRM':'Bv7_2014_GLRRM' }
#
# available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330', 'GERBL2_2014_STO_330_GLRRM', 'GERBL2_2014BOC_RCP45_GLRRM', 'Bv7_2014_GLRRM']
#
# baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330', 'GERBL2_2014_STO_330_GLRRM': 'GERBL2_2014_STO_330_GLRRM', 'GERBL2_2014BOC_RCP45_GLRRM':'GERBL2_2014BOC_RCP45_GLRRM',  'Bv7_2014_GLRRM':'Bv7_2014_GLRRM' }
#
# baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014', 'Bv7_2014_GLRRM'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_STO_330_GLRRM' ], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014BOC_RCP45_GLRRM',]}

available_plans=['OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboD_RCP45' ]

plans_ts_dct={'hist':['OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD'], 'sto':['GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_STO_330'], 'cc':['GERBL2_2014BOC_RCP45','GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45' ]}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330':'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD':'GERBL2_2014_ComboD', 'GERBL2_2014_ComboD_RCP45':'GERBL2_2014_ComboD_RCP45' }

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'

