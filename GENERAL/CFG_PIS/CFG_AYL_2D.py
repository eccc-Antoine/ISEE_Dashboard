import os

name = 'Agriculture Yield Loss'

type = '2D_not_tiled'

dct_var = {'VAR1': 'Average Yield Loss for all crops'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat = {'VAR1': ['sum']}

# normal mean higher is better
var_direction = {'Average Yield Loss for all crops': 'inverse'}

units = '$'

multiplier = 1

available_years_hist=list(range(1962, 2021))
available_years_future=list(range(2011, 2071))

divided_by_country = False

available_sections = ['SLR_DS', 'SLR_US']

sect_dct = {'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US'] }

available_plans=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45']

plans_ts_dct={'hist':['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45']}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'