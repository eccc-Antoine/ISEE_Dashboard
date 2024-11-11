import os

name='Wetland class area (LOSLR)'

type='2D_tiled'

dct_var={'VAR1':'Open Water', 'VAR2':'Submerged Aquatic Vegetation', 'VAR3':'Emergent Marsh', 'VAR4':'Wet Meadow', 'VAR5':'Swamp', 'VAR6':'Upland', 'VAR7':'Total Wetland Area'}

dct_var={'VAR1': 'Open Water', 'VAR2': 'MP_V', 'VAR3': 'MP', 'VAR4': 'MPP', 'VAR5': 'PH', 'VAR6': 'PH_A', 'VAR7': 'MARBU', 'VAR8': 'MARBO', 'VAR9': 'FORET_H', 'VAR10': 'URBAIN', 'VAR11':'IND', 'VAR12':'TOTAL_WETLANDS'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1': ['sum'], 'VAR2': ['sum'], 'VAR3': ['sum'], 'VAR4': ['sum'], 'VAR5': ['sum'], 'VAR6': ['sum'], 'VAR7': ['sum'], 'VAR8': ['sum'], 'VAR9': ['sum'], 'VAR10': ['sum'], 'VAR11':['sum'], 'VAR12':['sum']}

#normal mean higher is better
var_direction={'Open Water':'normal', 'MP_V':'normal', 'MP':'normal', 'MPP':'normal', 'PH':'normal', 'PH_A':'normal', 'MARBU':'normal', 'MARBO':'normal', 'FORET_H':'normal', 'URBAIN':'normal', 'IND':'normal', 'TOTAL_WETLANDS':'normal'}

units='Hectares'

multiplier=0.01

available_years=list(range(1962, 2021))

divided_by_country=False

available_sections=['SLR_DS', 'SLR_US']

sect_dct = {'St.Lawrence River downstream': ['SLR_DS'], 'St.Lawrence River upstream': ['SLR_US'] }

available_plans=['Bv7', 'OBS']

plan_dct={'Bv7': 'Bv7', 'Observation':'OBS'}

available_baselines=[]

baseline_dct={}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'

# available_plans=['Bv7_2014', 'Bv7', 'OBS']
#
# plan_dct={'Bv7_2014':'Bv7_2014' , 'Bv7': 'Bv7', 'Observation':'OBS'}
#
# available_baselines=['Bv7_GERBL1']
#
# baseline_dct={'Bv7_GERBL1':'Bv7_GERBL1'}
#
# available_stats = ['sum', 'mean']
#
# id_column_name = 'PT_ID'