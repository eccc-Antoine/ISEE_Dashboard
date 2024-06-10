import streamlit as st
import numpy as np # np mean, np random
import pandas as pd # read csv, df manipulation
#pd.options.mode.copy_on_write = True
pd.set_option('mode.chained_assignment', None)
import plotly.express as px # interactive charts
import os
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DASH as CFG_DASHBOARD
from DASHBOARDS.UTILS import DASHBOARDS_UTILS as UTILS
from DASHBOARDS.ISEE import ISEE_DASH_0_1 as MAIN
import geopandas as gpd
import json
import folium as f
from folium import plugins
import branca.colormap as cm
import requests
import sys
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import math



qp = st.query_params
if qp:
    #st.json(qp.to_dict())
    st.write(f'Processing tile {qp["data"]} ...')

# df_PI=MAIN.df_PI
#
# df_PI['YEAR']=df_PI['YEAR'].astype(str)
# st.dataframe(df_PI.style)

df_folder_base=os.path.join(MAIN.folder, MAIN.PI_code, 'YEAR', 'PT_ID',  MAIN.baseline_code)
pt_id_file_base=os.path.join(df_folder_base, f'{MAIN.var}_{MAIN.PI_code}_YEAR_{MAIN.baseline_code}_{int(qp["data"])}_PT_ID_{np.min(MAIN.unique_PI_CFG.available_years)}_{np.max(MAIN.unique_PI_CFG.available_years)}{MAIN.CFG_DASHBOARD.file_ext}')
df_base=UTILS.prep_data_map(pt_id_file_base, MAIN.start_year3, MAIN.end_year3, 'PT_ID', 'LAT', 'LON', MAIN.stat3, MAIN.Variable, MAIN.unique_pi_module_name)

df_base = df_base.sort_values(by='LAT')
# df_base['tile_mock']=df_base['PT_ID']/1000000
# df_base['tile_mock']=df_base['tile_mock'].apply(math.floor)
# df_base=df_base.loc[df_base['tile_mock']==int(qp["data"])]
# print(list(df_base))
# print(df_base.head())
# print(len(df_base))
# print(df_base.tail())



df_folder_plan=os.path.join(MAIN.folder, MAIN.PI_code, 'YEAR', 'PT_ID',  MAIN.ze_plan_code)
pt_id_file_plan=os.path.join(df_folder_plan, f'{MAIN.var}_{MAIN.PI_code}_YEAR_{MAIN.ze_plan_code}_{int(qp["data"])}_PT_ID_{np.min(MAIN.unique_PI_CFG.available_years)}_{np.max(MAIN.unique_PI_CFG.available_years)}{MAIN.CFG_DASHBOARD.file_ext}')
df_plan=UTILS.prep_data_map(pt_id_file_plan, MAIN.start_year3, MAIN.end_year3, 'PT_ID', 'LAT', 'LON', MAIN.stat3, MAIN.Variable, MAIN.unique_pi_module_name)

# df_plan = df_plan.sort_values(by='LAT')
# df_plan['tile_mock']=df_plan['PT_ID']/1000000
# df_plan['tile_mock']=df_plan['tile_mock'].apply(math.floor)
# df_plan=df_plan.loc[df_plan['tile_mock']==int(qp["data"])]


df_both=df_base.merge(df_plan, on=['PT_ID', 'LAT', 'LON'], how='outer', suffixes=('_base', '_plan'))
if MAIN.diff_type2==f'Values ({MAIN.unit_dct[MAIN.PI_code]})':
    df_both['diff']=df_both[f'{MAIN.Variable}_plan']-df_both[f'{MAIN.Variable}_base']
else:
    df_both['diff']=((df_both[f'{MAIN.Variable}_plan']-df_both[f'{MAIN.Variable}_base'])/df_both[f'{MAIN.Variable}_base'])*100

df_both['diff']=df_both['diff'].round(3)
df_both.dropna(subset = ['diff'], inplace=True)


fig=UTILS.plot_map_plotly(MAIN.PIs, MAIN.Variable, df_both, 'LON', 'LAT', 'PT_ID', MAIN.unique_pi_module_name, f'{MAIN.ze_plan} minus {MAIN.Baseline}', 'diff')
#fig=UTILS.plot_map_plotly(PIs, Variable, df_both, 'LAT', 'LON', 'PT_ID', unique_pi_module_name, f'{ze_plan} minus {Baseline}', 'diff')
st.plotly_chart(fig, use_container_width=True)


# m=UTILS.plot_map_folium(MAIN.PIs, MAIN.Variable, df_both, 'LAT', 'LON', 'PT_ID', MAIN.unique_pi_module_name, f'{MAIN.ze_plan} minus {MAIN.Baseline}', 'diff')
#
# UTILS.folium_static(m, 1200, 700)