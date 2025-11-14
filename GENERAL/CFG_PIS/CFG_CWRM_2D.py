import os

name='Wetland class area'
pi_code='CWRM_2D'
type='2D_tiled'

dct_var={'VAR1':'Open Water', 'VAR2':'Submerged Aquatic Vegetation', 'VAR3':'Emergent Marsh', 'VAR4':'Wet Meadow', 'VAR5':'Swamp', 'VAR6':'Upland', 'VAR7':'Total Wetland Area'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1':['sum'],'VAR2':['sum'],'VAR3':['sum'],'VAR4':['sum'],'VAR5':['sum'],'VAR6':['sum'],'VAR7':['sum'],}

#normal mean higher is better
var_direction={'Open Water':'normal', 'Submerged Aquatic Vegetation':'normal', 'Emergent Marsh':'normal', 'Wet Meadow':'normal', 'Swamp':'normal', 'Upland':'normal', 'Total Wetland Area':'normal'}

units='Hectares'

multiplier=0.01

available_years_hist=list(range(1962, 2021))
available_years_future=list(range(2012, 2071))

divided_by_country=False

available_sections=['LKO', 'USL_US', 'USL_DS']

sect_dct={'Lake Ontario':['LKO'], 'Upper St.Lawrence upstream':['USL_US'], 'Lake St.Lawrence':['USL_DS']}

available_plans=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_STO_330',
                 'PreProject_STO_330', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboD_STO_330',
                 'GERBL2_2014_ComboA','GERBL2_2014_ComboA_RCP45','GERBL2_2014_ComboA_STO_330']

plans_ts_dct={'hist':['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboA'],
              'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboA_STO_330'],
              'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboA_RCP45']}

plans_hist=['PreProjectHistorical', 'OBS', 'Bv7_2014', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'GERBL2_2014_ComboA']

plan_dct={'PreProjectHistorical':'PreProjectHistorical', 'OBS':'OBS', 'Bv7_2014':'Bv7_2014', 'Bv7_2014_ComboC':'Bv7_2014_ComboC', 'GERBL2_2014_ComboA':'GERBL2_2014_ComboA', 'GERBL2_2014_ComboD':'GERBL2_2014_ComboD',
          'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'PreProject_RCP45':'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45':'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45':'GERBL2_2014_ComboD_RCP45', 'GERBL2_2014_ComboA_RCP45':'GERBL2_2014_ComboA_RCP45',
          'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_STO_330': 'PreProject_STO_330', 'GERBL2_2014_ComboC_STO_330':'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330':'GERBL2_2014_ComboD_STO_330', 'GERBL2_2014_ComboA_STO_330':'GERBL2_2014_ComboA_STO_330'}

available_baselines=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330', 'PreProject_RCP45', 'PreProject_STO_330']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical' , 'Bv7_2014':'Bv7_2014', 'GERBL2_2014BOC_RCP45':'GERBL2_2014BOC_RCP45', 'GERBL2_2014_STO_330':'GERBL2_2014_STO_330', 'PreProject_RCP45':'PreProject_RCP45', 'PreProject_STO_330':'PreProject_STO_330'}

baseline_ts_dct={'hist':['PreProjectHistorical', 'Bv7_2014'], 'sto':['GERBL2_2014_STO_330', 'PreProject_STO_330'], 'cc':['GERBL2_2014BOC_RCP45', 'PreProject_RCP45']}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'
