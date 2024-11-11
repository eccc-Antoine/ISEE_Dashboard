import os

name='Number of Flooded Buildings'

type='2D_not_tiled'

#dct_var={'VAR1': 'Primary residential buildings', 'VAR2': 'Secondary residential buildings', 'VAR3': 'All residential buildings' }

dct_var = {'VAR1': 'Accessory buildings (boolean)',
	   'VAR2': 'Accessory building (Nb of QMs)',
	   'VAR3': 'Agricultural buildings (boolean)',
	   'VAR4': 'Agricultural buildings (Nb of QMs)',
	   'VAR5': 'Strategic assets buildings (boolean)',
	   'VAR6': 'Strategic assets buildings (Nb of QMs)',
	   'VAR7': 'Non-categorized (boolean)',
	   'VAR8': 'Non-categorized (Nb of QMs)',
	   'VAR9': 'Boathouse buildings (boolean)',
	   'VAR10': 'Boathouse buildings (Nb of QMs)',
	   'VAR11': 'Commercial buildings (boolean)',
	   'VAR12': 'Commercial buildings (Nb of QMs)',
	   'VAR13': 'Industrial buildings (boolean)',
	   'VAR14': 'Industrial buildings (Nb of QMs)',
	   'VAR15': 'Infrastructure buildings (boolean)',
	   'VAR16': 'Infrastructure buildings (Nb of QMs)',
	   'VAR17': 'Government-owned buildings (boolean)',
	   'VAR18': 'Government-owned buildings (Nb of QMs)',
	   'VAR19': 'Recreational buildings (boolean)',
	   'VAR20': 'Recreational buildings (Nb of QMs)',
	   'VAR21': 'Residential buildings (boolean)',
	   'VAR22': 'Residential buildings (Nb of QMs)'}

# need to be 'mean' or 'sum', values need to be a list even if there is only one item
var_agg_stat={'VAR1': ['sum'],
	   'VAR2': ['sum'],
	   'VAR3': ['sum'],
	   'VAR4': ['sum'],
	   'VAR5': ['sum'],
	   'VAR6': ['sum'],
	   'VAR7': ['sum'],
	   'VAR8': ['sum'],
	   'VAR9': ['sum'],
	   'VAR10': ['sum'],
	   'VAR11': ['sum'],
	   'VAR12': ['sum'],
	   'VAR13': ['sum'],
	   'VAR14': ['sum'],
	   'VAR15': ['sum'],
	   'VAR16': ['sum'],
	   'VAR17': ['sum'],
	   'VAR18': ['sum'],
	   'VAR19': ['sum'],
	   'VAR20': ['sum'],
	   'VAR21': ['sum'],
	   'VAR22': ['sum']}

#normal mean higher is better
var_direction={'VAR1': 'inverse',
	   'VAR2': 'inverse',
	   'VAR3': 'inverse',
	   'VAR4': 'inverse',
	   'VAR5': 'inverse',
	   'VAR6': 'inverse',
	   'VAR7': 'inverse',
	   'VAR8': 'inverse',
	   'VAR9': 'inverse',
	   'VAR10': 'inverse',
	   'VAR11': 'inverse',
	   'VAR12': 'inverse',
	   'VAR13': 'inverse',
	   'VAR14': 'inverse',
	   'VAR15': 'inverse',
	   'VAR16': 'inverse',
	   'VAR17': 'inverse',
	   'VAR18': 'inverse',
	   'VAR19': 'inverse',
	   'VAR20': 'inverse',
	   'VAR21': 'inverse',
	   'VAR22': 'inverse'}

units=' '

multiplier=1

available_years=list(range(1962, 2021))

divided_by_country=True

available_sections=['SLR_DS_CAN', 'SLR_US_CAN', 'USL_DS_US', 'USL_DS_CAN', 'USL_US_US',
 'USL_US_CAN', 'LKO_US', 'LKO_CAN']

# available_sections=['LKO']

sect_dct={'Lake Ontario Canada':['LKO_CAN'],
    'Lake Ontario United States':['LKO_US'],
    'Upper St.Lawrence upstream Canada ':['USL_US_CAN'],
    'Upper St.Lawrence upstream United States ':['USL_US_US'],
    'Lake St.Lawrence Canada':['USL_DS_CAN'],
    'Lake St.Lawrence United States':['USL_DS_US'],
    'St.Lawrence River downstream Canada': ['SLR_DS_CAN'],
    'St.Lawrence River upstreamn Canada': ['SLR_US_CAN']}


available_plans=['OBS', 'Bv7_GERBL1']

plan_dct={'OBS':'OBS', 'Bv7_GERBL1':'Bv7_GERBL1'}

available_baselines=['PreProjectHistorical']

baseline_dct={'PreProjectHistorical':'PreProjectHistorical'}

available_stats = ['sum', 'mean']

id_column_name = 'PT_ID'