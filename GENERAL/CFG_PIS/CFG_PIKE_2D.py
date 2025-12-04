import pandas as pd
import os

name='Northern Pike habitat'
pi_code='PIKE_2D'
type='2D_tiled'

dct_var = {'VAR1' : 'Area suitable for spawning and embryo-larval development',
	   'VAR2' : 'Area suitable for spawning'}

#normal mean higher is better (normal or inverse)
var_direction={'Area suitable for spawning and embryo-larval development':'normal', 'Area suitable for spawning':'normal'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'], 'VAR2':['sum']}

units='Hectares'

multiplier=1

available_years_hist=list(range(1962, 2021))
available_years_future=list(range(2012, 2071))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS', 'SLR_DS', 'SLR_US']

sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS'], 'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US']}

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