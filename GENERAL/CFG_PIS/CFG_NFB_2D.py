import os

name='Buildings at risk'
pi_code='NFB_2D'
type='2D_not_tiled'

# dct_var = {'VAR1': 'Accessory buildings (boolean)',
# 	   'VAR2': 'Accessory building (Nb of QMs)',
# 	   'VAR3': 'Strategic assets buildings (boolean)',
# 	   'VAR4': 'Strategic assets buildings (Nb of QMs)',
# 	   'VAR5': 'Non-residential (boolean)',
# 	   'VAR6': 'Non-residential (Nb of QMs)',
# 	   'VAR7': 'Residential (boolean)',
# 	   'VAR8': 'Residential (Nb of QMs)',
# 	   'VAR9': 'Total buildings (boolean)',
# 	   'VAR10': 'Total buildings (Nb of QMs)'}


dct_var = { 	   'VAR7': 'Residential (boolean)',
 	   'VAR8': 'Residential (Nb of QMs)',
	   'VAR9': 'Total buildings (boolean)',
	   'VAR10': 'Total buildings (Nb of QMs)'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
# var_agg_stat={'VAR1': ['sum'],
# 	   'VAR2': ['sum'],
# 	   'VAR3': ['sum'],
# 	   'VAR4': ['sum'],
# 	   'VAR5': ['sum'],
# 	   'VAR6': ['sum'],
# 	   'VAR7': ['sum'],
# 	   'VAR8': ['sum'],
# 	   'VAR9': ['sum'],
# 	   'VAR10': ['sum']}

var_agg_stat={'VAR7': ['sum'],
 	   'VAR8': ['sum'],
	   'VAR9': ['sum'],
	   'VAR10': ['sum']}


#normal mean higher is better
# var_direction={'Accessory buildings (boolean)': 'inverse',
# 	   'Accessory building (Nb of QMs)': 'inverse',
# 	   'Strategic assets buildings (boolean)': 'inverse',
# 	   'Strategic assets buildings (Nb of QMs)': 'inverse',
# 	   'Non-residential (boolean)': 'inverse',
# 	   'Non-residential (Nb of QMs)': 'inverse',
# 	   'Residential (boolean)': 'inverse',
# 	   'Residential (Nb of QMs)': 'inverse',
# 	   'Total buildings (boolean)': 'inverse',
# 	   'Total buildings (Nb of QMs)': 'inverse'}

var_direction={ 	   'Residential (boolean)': 'inverse',
 	   'Residential (Nb of QMs)': 'inverse',
	   'Total buildings (boolean)': 'inverse',
	   'Total buildings (Nb of QMs)': 'inverse'}

units=' '

multiplier=1

available_years_hist=list(range(1962, 2021))
available_years_future=list(range(2011, 2071))

divided_by_country=True

available_sections=['SLR_DS_CAN', 'USL_DS_US', 'USL_DS_CAN', 'USL_US_US',
 'USL_US_CAN', 'LKO_US', 'LKO_CAN'] #'SLR_US_CAN',

sect_dct={'Lake Ontario Canada':['LKO_CAN'],
    'Lake Ontario United States':['LKO_US'],
    'Upper St.Lawrence upstream Canada':['USL_US_CAN'],
    'Upper St.Lawrence upstream United States':['USL_US_US'],
    'Lake St.Lawrence Canada':['USL_DS_CAN'],
    'Lake St.Lawrence United States':['USL_DS_US'],
    'St.Lawrence River downstream Canada': ['SLR_DS_CAN']}
    #'St.Lawrence River upstream Canada': ['SLR_US_CAN']}


available_plans=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'OBS',
                 'PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45',
                 'PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330']

plans_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'OBS'],
              'sto':['PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330'],
              'cc':['PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45']}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB']

plan_dct={'PreProjectHistorical':'PreProject', 'OBS':'OBS', 'Bv7_2014':'2014', 'Bv7_2014_ComboC':'ComboC', 'GERBL2_2014_ComboD':'ComboD', 'GERBL2_2014_ComboA':'ComboA', 'GERBL2_2014_ComboB':'ComboB',
          'GERBL2_2014BOC_RCP45':'2014_CC', 'PreProject_RCP45':'PreProject_CC', 'GERBL2_2014_ComboC_RCP45':'ComboC_CC', 'GERBL2_2014_ComboD_RCP45':'ComboD_CC', 'GERBL2_2014_ComboA_RCP45':'ComboA_CC', 'GERBL2_2014_ComboB_RCP45':'ComboB_CC',
          'GERBL2_2014_STO_330':'2014_STO', 'PreProject_STO_330': 'PreProject_STO', 'GERBL2_2014_ComboC_STO_330':'ComboC_STO', 'GERBL2_2014_ComboD_STO_330':'ComboD_STO', 'GERBL2_2014_ComboA_STO_330':'ComboA_STO', 'GERBL2_2014_ComboB_STO_330':'ComboB_STO'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProject' , 'Bv7_2014':'2014',
              'GERBL2_2014BOC_RCP45':'2014_CC', 'PreProject_RCP45':'PreProject_CC',
              'GERBL2_2014_STO_330':'2014_STO', 'PreProject_STO_330':'PreProject_STO'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'