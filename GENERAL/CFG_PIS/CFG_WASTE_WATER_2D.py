import os

name='Waste Water'
pi_code='WASTE_WATER_2D'
type='2D_not_tiled'

dct_var={'VAR1' : 'Occurrence of impact', 'VAR2':'Index'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'], 'VAR2':['mean']}

#normal mean higher is better
var_direction={'Occurrence of impact' : 'inverse', 'Index': 'inverse'}

units=''

multiplier=1

available_years_hist=list(range(1961, 2021))
available_years_future=list(range(2011, 2071))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'SLR_DS']

sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'St.Lawrence River downstream':['SLR_DS']}

available_plans=['PreProjectHistorical', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD',
                'PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45',
                'PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330']

plans_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD'],
              'sto':['PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330'],
              'cc':['PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45']}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB']

plan_dct={'PreProjectHistorical':'PreProject',  'Bv7_2014':'2014', 'Bv7_2014_ComboC':'ComboC', 'GERBL2_2014_ComboD':'ComboD',
          'GERBL2_2014BOC_RCP45':'2014_CC', 'PreProject_RCP45':'PreProject_CC', 'GERBL2_2014_ComboC_RCP45':'ComboC_CC', 'GERBL2_2014_ComboD_RCP45':'ComboD_CC',
          'GERBL2_2014_STO_330':'2014_STO', 'PreProject_STO_330': 'PreProject_STO', 'GERBL2_2014_ComboC_STO_330':'ComboC_STO', 'GERBL2_2014_ComboD_STO_330':'ComboD_STO'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProject' , 'Bv7_2014':'2014',
              'GERBL2_2014BOC_RCP45':'2014_CC', 'PreProject_RCP45':'PreProject_CC',
              'GERBL2_2014_STO_330':'2014_STO', 'PreProject_STO_330':'PreProject_STO'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['sum']

id_column_name = 'PT_ID'