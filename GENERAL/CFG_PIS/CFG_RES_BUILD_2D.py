import os

name='Residential building damage'

type='2D_not_tiled'

dct_var={'VAR1':'Structural damages', 'VAR2':'Material damages', 'VAR3':'Total damage'}

units='K$ CAN'

available_years=list(range(1926, 2017))

available_sections=['LKO_CAN', 'USL_CAN']

available_plans=['Alt_1', 'Alt_2']

available_baselines=['Baseline']

available_stats=['sum', 'mean']