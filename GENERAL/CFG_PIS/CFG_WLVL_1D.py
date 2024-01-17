import os
import pandas as pd
import numpy as np

name='Water levels'

type='1D'

dct_var={'VAR1':'Yearly minimum water level', 'VAR2':'Yearly mean water level', 'VAR3':'Yearly maximum water level'}

units='meters (IGLD85)'

available_years=list(range(1900, 2021))

available_sections=['LKO', 'USL_UP', 'USL_DN', 'SLR_UP', 'SLR_DN']

dct_station_section={'LKO':'ont', 'USL_UP':'broc', 'USL_DN':'morr', 'SLR_UP':'ptcl', 'SLR_DN':'sorl'}

available_plans=['Bv7_policy_1025_Flim_skipT1_add3T_NG_historical_1900_2020', 'Bv7_policy_1025_NG_historical_1900_2020' ]

available_baselines=['Bv7_baseline_NG_historical_1900_2020']

available_stats=['mean']

GLRRM_name='mlv'
GLRRM_units='m'