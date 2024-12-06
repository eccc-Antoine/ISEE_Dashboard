import os

name = 'Flooded roads'

type = '2D_not_tiled'

dct_var = {'VAR1': 'Primary roads (Nb of QMs)',
           #'VAR2': 'Secondary roads (Nb of QMs)',
           #'VAR3': 'Tertiary roads (Nb of QMs)',
           #'VAR4': 'Unclassified roads (Nb of QMs)',
           'VAR5': 'All roads (Nb of QMs)',
           'VAR6': 'Primary roads (Lengh in m)',
           #'VAR7': 'Secondary roads (Lenght in m)',
           #'VAR8': 'Tertiary roads (Lenght in m)',
           #'VAR9': 'Unclassified roads (Lenght in m)',
           'VAR10': 'All roads (Lenght in m)'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat = {'VAR1': ['sum'],
           #'VAR2': ['sum'],
           #'VAR3': ['sum'],
           #'VAR4': ['sum'],
           'VAR5': ['sum'],
           'VAR6': ['sum'],
           #'VAR7': ['sum'],
           #'VAR8': ['sum'],
           #'VAR9': ['sum'],
           'VAR10': ['sum']}

# normal mean higher is better
var_direction = {'Primary roads (Nb of QMs)': 'inverse',
           #'Secondary roads (Nb of QMs)': 'inverse',
           #'Tertiary roads (Nb of QMs)': 'inverse',
           #'Unclassified roads (Nb of QMs)': 'inverse',
           'All roads (Nb of QMs)': 'inverse',
           'Primary roads (Lengh in m)': 'inverse',
           #'Secondary roads (Lenght in m)': 'inverse',
           #'Tertiary roads (Lenght in m)': 'inverse',
           #'Unclassified roads (Lenght in m)': 'inverse',
           'All roads (Lenght in m)': 'inverse'}

units = ''

multiplier = 1

available_years_hist=list(range(1961, 2021))
available_years_future=list(range(2011, 2071))

divided_by_country = False

available_sections = ['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']

sect_dct = {'Lake Ontario': ['LKO'], 'Upper St.Lawrence upstream': ['USL_US'], 'Lake St.Lawrence': ['USL_DS'], 'St.Lawrence River upstream':['SLR_US'], 'St.Lawrence River downstream':['SLR_DS']}

available_plans=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330']

plans_ts_dct={'hist':['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_ComboC_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45']}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330':'GERBL2_2014_ComboC_STO_330'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'