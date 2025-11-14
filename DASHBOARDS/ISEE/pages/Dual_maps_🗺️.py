import streamlit as st
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import os
import importlib
from pathlib import Path
import traceback
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
if 'has_resetted' not in st.session_state:
    st.session_state['has_resetted'] = False

if 'PI_code' not in st.session_state:
    st.session_state['PI_code'] = pis_code[0]
    st.session_state['selected_pi'] = default_PI

if 'ts_code' not in st.session_state:
    st.session_state['ts_code'] = tss_code[0]
    st.session_state['selected_timeseries'] = default_ts

if 'unique_PI_CFG' not in st.session_state:
    PI_code = st.session_state['PI_code']
    st.session_state['unique_PI_CFG'] = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{PI_code}')

if 'azure_container' not in st.session_state:
    # connect to Azur blob storage
    blob_service_client = BlobServiceClient(CFG_DASHBOARD.azure_url, credential = CFG_DASHBOARD.access_key)
    container = blob_service_client.get_container_client('dukc-db')
    st.session_state['azure_container'] = container
    # If azure container is not in session state, it means it's the first time loading a page, since we have this on all pages
    UTILS.initialize_session_state()

if 'baseline_code' not in st.session_state:
    st.session_state['baseline_code'] = None

if 'gdf_grille_base' not in st.session_state:
    st.session_state['gdf_grille_base'] = None

# Change PI or Timeserie
def update_PI_code():
    st.session_state['selected_pi'] = st.session_state['_selected_pi']
    selected_pi_name = st.session_state['selected_pi']
    pi_code = [key for key, value in pi_dct.items() if value == selected_pi_name]
    st.session_state['PI_code'] = pi_code[0]
    st.session_state['unique_PI_CFG'] = importlib.import_module(f"GENERAL.CFG_PIS.CFG_{pi_code[0]}")

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
        st.subheader('**Parameters**')
        old_PI_code, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code=render_column1_simple()
        var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]

        if unique_PI_CFG.var_agg_stat[var][0]=='sum':
            stat_list = unique_PI_CFG.var_agg_stat[var] + ['mean', 'min', 'max']
            stat = st.selectbox("Select a way to aggregate values for the selected period",
                                     stat_list, index=stat_list.index(st.session_state['selected_stat']),
                                     key='_selected_stat', on_change=UTILS.update_session_state, args=('selected_stat', ))
        else:
            stat_list = unique_PI_CFG.var_agg_stat[var] + ['min', 'max']
            stat = st.selectbox("Select a way to aggregate values for the selected period",
                                stat_list, index=stat_list.index(st.session_state['selected_stat']),
                                key='_selected_stat', on_change=UTILS.update_session_state, args=('selected_stat', ))

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
        st.subheader('**Plot**')
        # Compare with dual Maps
        available_plans = unique_PI_CFG.plans_ts_dct[ts_code]
        baseline, candidate = st.columns(2)
        baselines = unique_PI_CFG.baseline_ts_dct[ts_code]
        if len(baselines)==0 or len(available_plans)==0:
            st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')
        else:
            with baseline:
                Baseline = st.selectbox("Select a reference plan to display", baselines,
                                            index=baselines.index(st.session_state['Baseline']),
                                            key='_Baseline',on_change=UTILS.update_session_state, args=('Baseline',))
            with candidate:
                ze_plan = st.selectbox("Select a regulation plan to compare with reference plan", available_plans,
                                       index=available_plans.index(st.session_state['ze_plan']),
                                       key='_ze_plan',on_change=UTILS.update_session_state, args=('ze_plan', ))

            baseline_code = unique_PI_CFG.baseline_dct[Baseline]
            ze_plan_code = unique_PI_CFG.plan_dct[ze_plan]

            if unique_PI_CFG.type in ['2D_tiled','2D_not_tiled']:

                gdf_grille_base = UTILS.prep_for_prep_tiles_parquet(tiles_shp, df_PI, baseline_code, stat, var,
                                                                        unique_PI_CFG, start_year, end_year, st.session_state['azure_container'])
                st.session_state['gdf_grille_base'] = gdf_grille_base

                gdf_grille_plan = UTILS.prep_for_prep_tiles_parquet(tiles_shp, df_PI, ze_plan_code, stat, var,
                                                                        unique_PI_CFG, start_year, end_year, st.session_state['azure_container'])

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', Variable, unique_PI_CFG, 'TILE')
            else:
                if unique_PI_CFG.divided_by_country:
                    sct_shp = sct_poly_country
                else:
                    sct_shp = sct_poly

                gdf_grille_base = UTILS.prep_for_prep_1d(sct_shp, df_PI, baseline_code, stat,
                                                             var, unique_PI_CFG,
                                                             start_year, end_year, Baseline,
                                                             st.session_state['azure_container'])

                gdf_grille_plan = UTILS.prep_for_prep_1d(sct_shp, df_PI, ze_plan_code, stat,
                                                             var, unique_PI_CFG,
                                                             start_year, end_year, Baseline,
                                                             st.session_state['azure_container'])

                if baseline_code=='PreProjectHistorical':
                    st.write(':red[It is not possible to have values for PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', Variable, unique_PI_CFG, 'SECTION')

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
                    data=prepare_shapefile(gdf_grille_base,f'{PI_code}_{stat}_{var}_{start_year}_{end_year}_{ts_code}_{baseline_code}.shp'),
                    file_name="Baseline_map.zip",
                    mime="application/zip")
        with plan_button:
            # Add the download button
            st.download_button(
                        label="Candidate Map",
                        data=prepare_shapefile(gdf_grille_plan,f'{PI_code}_{stat}_{var}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}.shp'),
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

    old_ts_code = st.session_state['ts_code']
    ts_list = list(ts_dct.values())
    st.selectbox("Select a supply", ts_list, index=ts_list.index(ts_dct[st.session_state['ts_code']]), key='timeseries')
    update_timeseries()

    old_PI_code = st.session_state['PI_code']
    pi_list = list(pi_dct.values())
    pi_list.sort()
    st.selectbox("Select a Performance Indicator", pi_list,
                 index=pi_list.index(pi_dct[st.session_state['PI_code']]),
                 key='_selected_pi')
    update_PI_code()

    PI_code = st.session_state['PI_code']
    ts_code = st.session_state['ts_code']
    unique_PI_CFG = st.session_state['unique_PI_CFG']

    # If the user changed the PI or the timseries, update widgets
    if (old_PI_code != st.session_state['PI_code']) or (old_ts_code != st.session_state['ts_code']):
        UTILS.initialize_session_state()

    start_year, end_year, Variable = UTILS.MAIN_FILTERS_streamlit_simple(ts_code,
            unique_PI_CFG, Years=True, Variable=True)

    return old_PI_code, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code

try:
    function_for_tab3()
    st.session_state['has_resetted'] = False
except Exception as e:
    if not st.session_state['has_resetted']:
        st.warning('An error occurred, restarting the dashboard now...')
        st.error(traceback.format_exc())

        st.session_state['PI_code'] = pis_code[0]
        st.session_state['selected_pi'] = default_PI
        st.session_state['ts_code'] = tss_code[0]
        st.session_state['selected_timeseries'] = default_ts

        UTILS.initialize_session_state()
        st.session_state['has_resetted'] = True
        st.rerun()
    else:
        st.error('An error occurred and persisted. Please close the dashboard and open it again. If you are still not able to use the dashboard, please contact us and we will assist you. We are sorry for the inconvenience.')
        st.error(traceback.format_exc())

print('Execution time :', dt.now()-start)
print('----------------------------END----------------------------')