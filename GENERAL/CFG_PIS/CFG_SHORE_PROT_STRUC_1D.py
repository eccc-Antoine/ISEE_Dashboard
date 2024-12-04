import numpy

name='Shoreline Protection Structure'

type='1D'

dct_var={'VAR1': 'Wave overtopping (*10e-2)', 'VAR2': 'Wave overflow (*10e-4)'}

#normal mean higher is better
var_direction={'Wave overtopping (*10e-2)':'inverse', 'Wave overflow (*10e-4)':'inverse'}


# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['mean'], 'VAR2':['mean']}

units=''

multiplier=1

available_years_hist=list(range(1961, 2021))
available_years_future=list(range(2011, 2071))
divided_by_country=False

available_sections=['LKO']
#available_sections=['LKO', 'USL_US', 'SLR_US', 'SLR_DS']
#available_sections=['LKO', 'USL_US', 'SLR_US']

sect_dct={'Lake Ontario':['LKO']}

available_plans=[ 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330']
#available_plans=[ 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC']

plans_ts_dct={'hist':['Bv7_2014', 'Bv7_2014_ComboC'], 'sto':['GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_STO_330'], 'cc':['GERBL2_2014BOC_RCP45','GERBL2_2014_ComboC_RCP45']}
#plans_ts_dct={'hist':['OBS', 'Bv7_2014', 'Bv7_2014_ComboC']}

plans_hist=['PreProjectHistorical', 'Bv7_2014', 'Bv7_2014_ComboC']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330':'GERBL2_2014_ComboC_STO_330'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']
#available_baselines=['PreProjectHistorical', 'OBS', 'Bv7_2014']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}
#baseline_ts_dct={'hist':['PreProjectHistorical', 'OBS', 'Bv7_2014']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'

