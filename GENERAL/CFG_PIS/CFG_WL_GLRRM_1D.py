
name='Water Levels 1D (GLRRM)'

pi_code='WL_GLRRM_1D'

type='1D'

dct_var={'VAR1':'Yearly min water level', 'VAR2':'Yearly mean water level', 'VAR3':'Yearly max water level' }

#'normal' means higher is better
var_direction={'Yearly min water level':'normal', 'Yearly mean water level':'inverse', 'Yearly max water level':'inverse'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean'], 'VAR2':['mean'], 'VAR3':['mean']}

units='m'

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

available_plans=['PreProjectHistorical', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_STO_330',
                 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboD_STO_330',
                 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboB_STO_330']

plans_ts_dct={'hist':['PreProjectHistorical','Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB'],
              'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330'],
              'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45']}

plans_hist=['PreProjectHistorical', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014_ComboA':'GERBL2_2014_ComboA', 'GERBL2_2014_ComboD':'GERBL2_2014_ComboD', 'GERBL2_2014_ComboB':'GERBL2_2014_ComboB',
          'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45':'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboA_RCP45':'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45':'GERBL2_2014_ComboB_RCP45',
          'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_STO_330':'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330':'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboA_STO_330':'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330':'GERBL2_2014_ComboB_STO_330'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['mean']


