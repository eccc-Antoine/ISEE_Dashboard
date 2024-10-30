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
#from DASHBOARDS.ISEE import ISEE_DASH_0_1 as MAIN
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
import ast

#qp = st.experimental_get_query_params()

qp = st.query_params
print(qp)

if 'pi_code' in qp and 'data' in qp:


    st.cache_data.clear()
    st.cache_resource.clear()




    for key in st.session_state.keys():
        print(st.session_state[key])


    PI_code = qp['pi_code']
    data = qp['data']
    folder = qp['folder']
    baseline_code = qp['baseline_code']
    var = qp['var']
    years = qp['years']
    ext = qp['ext']
    start_year=qp['start_year']
    end_year = qp['end_year']
    stat= qp['stat']
    Variable=qp['Variable']
    unique_pi_module_name=qp['unique_pi_module_name']
    ze_plan_code=qp['ze_plan_code']
    unit_dct=qp['unit_dct']
    diff_type=qp['diff_type']
    ze_plan = qp['ze_plan']
    Baseline = qp['Baseline']
    pi_type=qp['pi_type']



    st.write(f'Difference of :blue[{PI_code} {Variable} {stat}] between :blue[{ze_plan} and {Baseline}] from :blue[{start_year} to {end_year}]\n for tile :blue[{data}] at each ISEE 10x10m grid node')

    years=years.replace('[','')
    years = years.replace(']','')
    years = years.replace(' ', '')
    years=years.split(',')
    years=[int(x) for x in years]
    #print(years)

    unit_dct=ast.literal_eval(unit_dct)

    # df_PI=MAIN.df_PI
    #
    # df_PI['YEAR']=df_PI['YEAR'].astype(str)
    # st.dataframe(df_PI.style)


    # my_dict = MAIN.CFG_DASHBOARD.dct_tile_sect
    # value_to_find = int(qp["data"]
    # keys_with_value = [key for key, value_list in my_dict.items() if value_to_find in value_list]
    #
    # print(keys_with_value)
    #
    # if len(keys_with_value)>1:
    #     if MAIN.unique_PI_CFG.divided_by_country=True:
    #         print('per country')

    df_folder_base=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  baseline_code)

    #pt_id_file_base=os.path.join(df_folder_base, f'{var}_{PI_code}_YEAR_{baseline_code}_{int(data)}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')

    print(type)
    if pi_type=='2D_not_tiled':
        pt_id_file_base = os.path.join(df_folder_base, f'{var}_{PI_code}_YEAR_{baseline_code}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_base=UTILS.prep_data_map(pt_id_file_base, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name, pi_type, int(data))

    else:
        pt_id_file_base = os.path.join(df_folder_base, f'{var}_{PI_code}_YEAR_{baseline_code}_{int(data)}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_base=UTILS.prep_data_map(pt_id_file_base, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name,pi_type, int(data))

    df_base = df_base.sort_values(by='LAT')
    # df_base['tile_mock']=df_base['PT_ID']/1000000
    # df_base['tile_mock']=df_base['tile_mock'].apply(math.floor)
    # df_base=df_base.loc[df_base['tile_mock']==int(qp["data"])]
    # print(list(df_base))
    # print(df_base.head())
    # print(len(df_base))
    # print(df_base.tail())

    df_folder_plan=os.path.join(folder, PI_code, 'YEAR', 'PT_ID', ze_plan_code)

    if pi_type == '2D_not_tiled':
        pt_id_file_plan = os.path.join(df_folder_plan, f'{var}_{PI_code}_YEAR_{ze_plan_code}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_plan=UTILS.prep_data_map(pt_id_file_plan, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name, pi_type, int(data))


    else:
        pt_id_file_plan=os.path.join(df_folder_plan, f'{var}_{PI_code}_YEAR_{ze_plan_code}_{int(data)}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_plan=UTILS.prep_data_map(pt_id_file_plan, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name, pi_type, int(data))

    # df_plan = df_plan.sort_values(by='LAT')
    # df_plan['tile_mock']=df_plan['PT_ID']/1000000
    # df_plan['tile_mock']=df_plan['tile_mock'].apply(math.floor)
    # df_plan=df_plan.loc[df_plan['tile_mock']==int(qp["data"])]


    # df_plan.to_csv(fr'H:\Projets\GLAM\Dashboard\debug\full_res_plan.csv' , sep=';', index=None)
    #
    # df_base.to_csv(fr'H:\Projets\GLAM\Dashboard\debug\full_res_base.csv' , sep=';', index=None)

    #df_both=df_base.merge(df_plan, on=['PT_ID', 'LAT', 'LON'], how='outer', suffixes=('_base', '_plan'))
    df_both=df_base.merge(df_plan, on=['PT_ID'], how='outer', suffixes=('_base', '_plan'))
    df_both=df_both.fillna(0)

    if diff_type==f'Values ({unit_dct[PI_code]})':
        df_both['diff']=df_both[f'{Variable}_plan']-df_both[f'{Variable}_base']
    else:
        df_both['diff']=((df_both[f'{Variable}_plan']-df_both[f'{Variable}_base'])/df_both[f'{Variable}_base'])*100

    df_both['diff']=df_both['diff'].round(3)
    df_both.dropna(subset = ['diff'], inplace=True)

    #df_both.to_csv(fr'P:\GLAM\Dashboard\debug\full_res_both_pre.csv' , sep=';', index=None)

    df_both=df_both.loc[df_both['diff']!=0]

    #df_both.to_csv(fr'P:\GLAM\Dashboard\debug\full_res_both.csv' , sep=';', index=None)


    lon_cols=[col for col in list(df_both) if 'LON' in col]
    lon_col=lon_cols[0]
    lat_cols=[col for col in list(df_both) if 'LAT' in col]
    lat_col=lat_cols[0]

    df_both['LAT']=np.where(df_both['LAT_base'] == 0, df_both['LAT_plan'], df_both['LAT_base'])
    df_both['LON']=np.where(df_both['LON_base'] == 0, df_both['LON_plan'], df_both['LON_base'])

    #print(df_both['LAT'])
    #print(df_both['LON'])

    #print(f'!!!!!! {len(df_both)}')
    fig=UTILS.plot_map_plotly(Variable, df_both, 'LON', 'LAT', 'PT_ID', unique_pi_module_name, f'{ze_plan} minus {Baseline}', 'diff')
    #print(fig)
    #fig=UTILS.plot_map_plotly(PIs, Variable, df_both, 'LAT', 'LON', 'PT_ID', unique_pi_module_name, f'{ze_plan} minus {Baseline}', 'diff')
    st.plotly_chart(fig, use_container_width=True)


# m=UTILS.plot_map_folium(MAIN.PIs, MAIN.Variable, df_both, 'LAT', 'LON', 'PT_ID', MAIN.unique_pi_module_name, f'{MAIN.ze_plan} minus {MAIN.Baseline}', 'diff')
#
# UTILS.folium_static(m, 1200, 700)