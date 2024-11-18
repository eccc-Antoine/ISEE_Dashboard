import os

name='Marsh Birds'

type='2D_not_tiled'

dct_var={'VAR1': 'Abundance', 'VAR2': 'Richness'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['mean']}

#normal mean higher is better
var_direction={'Abundance':'normal', 'Richness':'normal'}

units=' '

multiplier=1

available_years_hist=list(range(1962, 2021))
available_years_future=list(range(2012, 2071))

divided_by_country=False

available_sections=['LKO']

sect_dct={'Lake Ontario':['LKO']}

# available_plans=['1958DD', 'Bv7_2014', 'Bv7_GERBL1', 'GERBL2_2014_STO_330', 'PreProject_RCP45']
#
# plans_ts_dct={'hist':['1958DD', 'Bv7_2014', 'Bv7_GERBL1'], 'sto':['GERBL2_2014_STO_330'], 'cc':['PreProject_RCP45']}
#
# plans_hist=['1958DD', 'Bv7_2014', 'Bv7_GERBL1', 'PreProjectHistorical']
#
# #plan_dct={'1958DD':'1958DD', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1'}
#
# plan_dct={'1958DD':'1958DD', 'Bv7_2014':'Bv7_2014', 'Bv7_GERBL1':'Bv7_GERBL1', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45'}
#
# #available_baselines=['PreProjectHistorical']
#
# #baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}
#
# available_baselines=['PreProject_STO_330', 'PreProjectHistorical']
#
# baseline_dct={'PreProject_STO_330':'PreProject_STO_330', 'PreProjectHistorical':'PreProjectHistorical'}
#
# baseline_ts_dct={'hist':['PreProjectHistorical'], 'sto':['PreProject_STO_330'], 'cc':['PreProject_STO_330']}
#
# plans_future=[]


available_plans=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_STO_330', 'PreProject_STO_330']
#available_plans=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'PreProject_RCP45', 'GERBL2_2014_STO_330', 'PreProject_STO_330']

plans_ts_dct={'hist':['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}
#plans_ts_dct={'hist':['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['PreProject_RCP45']}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

#available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}
#baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['PreProject_RCP45']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'