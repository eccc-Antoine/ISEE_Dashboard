import streamlit as st  # web development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
pd.set_option('mode.chained_assignment', None)
import os
import importlib
from pathlib import Path
import sys
import io
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
import CFG_ISEE_DUCK as CFG_DASHBOARD
from DASHBOARDS.UTILS.pages import Dual_maps_utils as UTILS

from datetime import datetime as dt
from azure.storage.blob import BlobServiceClient
import warnings
warnings.filterwarnings('ignore')

start = dt.now()

def set_base_path():
    CFG_DASHBOARD.post_process_folder = CFG_DASHBOARD.post_process_folder_name

set_base_path()

st.set_page_config(
    page_title='ISEE Dashboard',
    page_icon='🏞️',
    layout='wide',
    initial_sidebar_state="collapsed")

folder = CFG_DASHBOARD.post_process_folder # Pas clair
pis_code = CFG_DASHBOARD.pi_list # PI list
tss_code=CFG_DASHBOARD.ts_list # Timeserie list

# Thoses files are in \\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\shapefiles\
sct_poly = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.sct_poly_name)
sct_poly_country = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.sct_poly_country_name)
tiles_shp = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.tiles_shp_name)

# Import PI configuration
pi_dct = {}
for pi in pis_code:
    pi_module_name = f'CFG_{pi}'
    PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    pi_dct[pi] = PI_CFG.name
del PI_CFG

# Pretty name of pi
pis = list(pi_dct.values())

ts_dct={'hist':'historical', 'sto':'stochastic', 'cc':'climate change'}

default_PI=next(iter(pi_dct.values()), None)
default_ts=next(iter(ts_dct.values()), None)

# State management
# Define which PI or timeserie to show by default
if 'PI_code' not in st.session_state:
    st.session_state['PI_code'] = pis_code[0]
    st.session_state['selected_pi'] = default_PI

if 'ts_code' not in st.session_state:
    st.session_state['ts_code'] = tss_code[0]
    st.session_state['selected_timeseries'] = default_ts

if 'baseline_code' not in st.session_state:
    st.session_state['baseline_code'] = None

if 'gdf_grille_base' not in st.session_state:
    st.session_state['gdf_grille_base'] = None

if 'unique_PI_CFG' not in st.session_state:
    PI_code = st.session_state['PI_code']
    st.session_state['unique_PI_CFG'] = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{PI_code}')

if 'azure_container' not in st.session_state:
    # connect to Azur blob storage
    blob_service_client = BlobServiceClient(CFG_DASHBOARD.azure_url, credential = CFG_DASHBOARD.access_key)
    container = blob_service_client.get_container_client('dukc-db')
    st.session_state['azure_container'] = container

# Change PI or Timeserie
def update_PI_code():
    selected_pi_name = st.session_state['selected_pi']
    pi_code = [key for key, value in pi_dct.items() if value == selected_pi_name]
    st.session_state['PI_code'] = pi_code[0]

def update_timeseries():
    selected_timeseries = st.session_state['timeseries']
    ts_code = [key for key, value in ts_dct.items() if value == selected_timeseries]
    st.session_state['ts_code'] = ts_code[0]

def prepare_shapefile(gdf_grille,shapefile_name):
    shapefile_data = UTILS.save_gdf_to_zip(gdf_grille,shapefile_name)
    return(shapefile_data)

def prepare_html(m):
    map_html = io.BytesIO()
    m.save(map_html, close_file=False)
    map_html.seek(0)
    return(map_html.getvalue())

st.title('Dual Maps 🗺️')
st.subheader('Select what you want to see on the left, select which plan you want to compare and display the maps on the right.', divider="gray")

st.session_state.gdf_grille_plan = None

def function_for_tab3():

    Col1, Col2 = st.columns([0.2, 0.8], gap='large')
    with Col1:
        old_PI_code, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code=render_column1_simple()
        var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]

        if unique_PI_CFG.var_agg_stat[var][0] =='sum':
            stat5 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var] + ['mean', 'min', 'max'], key='stat5', index=0)
        else:
            stat5 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var] + ['min', 'max'], key='stat5', index=0)

        if unique_PI_CFG.type in ['2D_tiled','2D_not_tiled']:
            division = 'TILE'
        else:
            division = 'SECTION'

        if 'df_PI_dualmaps' not in st.session_state:
            st.session_state['df_PI_dualmaps'] = UTILS.create_timeseries_database(f'test', PI_code, st.session_state['azure_container'],division)
        if (old_PI_code != PI_code):
            st.session_state['df_PI_dualmaps'] = UTILS.create_timeseries_database(f'test', PI_code, st.session_state['azure_container'],division)

        df_PI = st.session_state['df_PI_dualmaps']

    with Col2:

        baseline, candidate = st.columns(2)
        baselines = unique_PI_CFG.baseline_ts_dct[ts_code]

        with baseline:
            Baseline2 = st.selectbox("Select a reference plan to display", baselines)

        baseline_code = unique_PI_CFG.baseline_dct[Baseline2]
        available_plans = unique_PI_CFG.plans_ts_dct[ts_code]

        if len(baselines)==0 or len(available_plans)==0:
            st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

        else:
            with candidate:
                ze_plan2 = st.selectbox("Select a candidate plan to display", available_plans, key='ze_plan2', index=0)
            ze_plan_code = unique_PI_CFG.plan_dct[ze_plan2]
            var2 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]


            if unique_PI_CFG.type in ['2D_tiled','2D_not_tiled']:

                gdf_grille_base = UTILS.prep_for_prep_tiles_parquet(tiles_shp, df_PI, baseline_code, stat5, var,
                                                                        unique_PI_CFG, start_year, end_year, st.session_state['azure_container'])
                st.session_state['gdf_grille_base'] = gdf_grille_base

                gdf_grille_plan = UTILS.prep_for_prep_tiles_parquet(tiles_shp, df_PI, ze_plan_code, stat5, var,
                                                                        unique_PI_CFG, start_year, end_year, st.session_state['azure_container'])

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', Variable, unique_PI_CFG, 'TILE')
            else:
                if unique_PI_CFG.divided_by_country:
                    sct_shp = sct_poly_country
                else:
                    sct_shp = sct_poly

                gdf_grille_base = UTILS.prep_for_prep_1d(sct_shp, df_PI, baseline_code, stat5,
                                                             var, unique_PI_CFG,
                                                             start_year, end_year, Baseline2,
                                                             st.session_state['azure_container'])

                gdf_grille_plan = UTILS.prep_for_prep_1d(sct_shp, df_PI, ze_plan_code, stat5,
                                                             var2, unique_PI_CFG,
                                                             start_year, end_year, Baseline2,
                                                             st.session_state['azure_container'])

                if baseline_code=='PreProjectHistorical':
                    st.write(':red[It is not possible to have values for PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', Variable, unique_PI_CFG, 'SECTION')

            st.session_state['baseline_ready'] = True
            col_shape, col_html = st.columns(2,gap='small',width=600)
            with col_shape:
                st.write('Download as shapefile')
                col_map1, col_map2 = st.columns(2,gap=None,width=260)
                with col_map1:
                    baseline_button = st.container()

                with col_map2:
                    plan_button = st.container()
            with col_html:
                st.write('Download as HTML')
                maps_button = st.container()

            UTILS.folium_static(m, 1200, 700)

        with baseline_button:                # Add the download button
            st.download_button(
                    label="Baseline Map",
                    data=prepare_shapefile(gdf_grille_base,f'{PI_code}_{stat5}_{var}_{start_year}_{end_year}_{ts_code}_{baseline_code}.shp'),
                    file_name="Baseline_map.zip",
                    mime="application/zip")
        with plan_button:
            # Add the download button
            st.download_button(
                        label="Candidate Map",
                        data=prepare_shapefile(gdf_grille_plan,f'{PI_code}_{stat5}_{var2}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}.shp'),
                        file_name="Plan_map.zip",
                        mime="application/zip")

        with maps_button:
            st.download_button(
                    label="Both Maps",
                    data=prepare_html(m),
                    file_name="map.html",
                    mime="text/html",
                    key='db_3', type='primary')

def render_column1_simple():

    st.selectbox("Select a supply", ts_dct.values(), key='timeseries',
                               on_change=update_timeseries)
    ts_code = st.session_state['ts_code']
    old_PI_code = st.session_state['PI_code']
    pi_list = list(pi_dct.values())
    pi_list.sort()
    st.selectbox("Select a Performance Indicator", pi_list, key='selected_pi')
    update_PI_code()

    PI_code = st.session_state['PI_code']

    st.session_state['unique_PI_CFG'] = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{PI_code}')
    unique_PI_CFG = st.session_state['unique_PI_CFG']

    start_year, end_year, Variable = UTILS.MAIN_FILTERS_streamlit_simple(ts_code,
            unique_PI_CFG, Years=True, Variable=True)

    return old_PI_code, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code

function_for_tab3()
print('Execution time :', dt.now()-start)
print('----------------------------END----------------------------')