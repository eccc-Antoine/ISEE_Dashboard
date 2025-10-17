import streamlit as st  # web development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
pd.set_option('mode.chained_assignment', None)
import os
import importlib
from pathlib import Path
import sys
import io
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DUCK as CFG_DASHBOARD
from DASHBOARDS.UTILS.pages import Dual_maps_utils as UTILS
import sys

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
unit_dct = {}
for pi in pis_code:
    pi_module_name = f'CFG_{pi}'
    PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    pi_dct[pi] = PI_CFG.name
    unit_dct[pi] = PI_CFG.units

# Pretty name of pi
pis = [pi_dct[pi] for pi in pis_code]

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

# Change PI or Timeserie
def update_PI_code():
    selected_pi_name = st.session_state['selected_pi']
    pi_code = [key for key, value in pi_dct.items() if value == selected_pi_name]
    st.session_state['PI_code'] = pi_code[0]

def update_timeseries():
    selected_timeseries = st.session_state['timeseries']
    ts_code = [key for key, value in ts_dct.items() if value == selected_timeseries]
    st.session_state['ts_code'] = ts_code[0]

st.title('Dual Maps 🗺️')
st.subheader('Select what you want to see on the left, select which plan you want to compare and display the maps on the right.', divider="gray")

st.session_state.gdf_grille_base = None
st.session_state.gdf_grille_plan = None

def function_for_tab3():

    Col1, Col2 = st.columns([0.2, 0.8], gap='large')
    with Col1:
        selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code=render_column1_simple()
        var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
        if unique_PI_CFG.var_agg_stat[var][0] =='sum':
            stat5 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var] + ['mean', 'min', 'max'], key='stat5', index=0)
        else:
            stat5 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var] + ['min', 'max'], key='stat5', index=0)

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

            if ts_code=='hist':
                years_list=unique_PI_CFG.available_years_hist
            else:
                years_list = unique_PI_CFG.available_years_future

            if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':

                gdf_grille_base = UTILS.prep_for_prep_tiles_duckdb_lazy(tiles_shp, folder, PI_code, baseline_code,
                                                                years_list, stat5, var,
                                                                unique_pi_module_name, start_year, end_year, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                gdf_grille_plan = UTILS.prep_for_prep_tiles_duckdb_lazy(tiles_shp, folder, PI_code, ze_plan_code,
                                                                years_list, stat5, var,
                                                                unique_pi_module_name, start_year, end_year, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', Variable,
                                                     unique_pi_module_name, unit_dct[PI_code], 'tile')

            else:
                if unique_PI_CFG.divided_by_country:
                    sct_shp = sct_poly_country
                else:
                    sct_shp = sct_poly

                gdf_grille_base = UTILS.prep_for_prep_1d(ts_code, unique_PI_CFG.sect_dct, sct_shp, folder,
                                                             PI_code, baseline_code, years_list, stat5,
                                                             var, unique_pi_module_name,
                                                             start_year, end_year, Baseline2, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                gdf_grille_plan = UTILS.prep_for_prep_1d(ts_code, unique_PI_CFG.sect_dct, sct_shp, folder,
                                                             PI_code, ze_plan_code, years_list, stat5,
                                                             var2, unique_pi_module_name,
                                                             start_year, end_year, Baseline2, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                if baseline_code=='PreProjectHistorical':
                    st.write(':red[It is not possible to have values for PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', Variable,
                                                      unique_pi_module_name, unit_dct[PI_code], 'SECTION')

            col_map1, col_map2, col_map3=st.columns(3,gap='small')

            with col_map1:
                shapefile_data = UTILS.save_gdf_to_zip(gdf_grille_base,
                                                           f'{PI_code}_{stat5}_{var}_{start_year}_{end_year}_{ts_code}_{baseline_code}.shp')
                # Add the download button
                st.download_button(
                        label="💾 Baseline Map as shapefile",
                        data=shapefile_data,
                        file_name="Baseline_map.zip",
                        mime="application/zip")

            with col_map2:
                map_html = io.BytesIO()
                m.save(map_html, close_file=False)
                map_html.seek(0)
                st.download_button(
                    label="💾 Both Maps as HTML",
                    data=map_html.getvalue(),
                    file_name="map.html",
                    mime="text/html",
                    key='db_3', type='primary')

            with col_map3:
                shapefile_data = UTILS.save_gdf_to_zip(gdf_grille_plan,
                                                           f'{PI_code}_{stat5}_{var2}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}.shp')
                # Add the download button
                st.download_button(
                        label="💾 Candidate Plan Map as shapefile",
                        data=shapefile_data,
                        file_name="Plan_map.zip",
                        mime="application/zip")

            UTILS.folium_static(m, 1200, 700)

def render_column1_simple():

    timeseries = st.selectbox("Select a supply", ts_dct.values(), key='timeseries',
                               on_change=update_timeseries)

    ts_code = st.session_state['ts_code']

    selected_pi=st.selectbox("Select a Performance Indicator", list(pi_dct.values()), key='selected_pi', on_change=update_PI_code)

    PI_code = st.session_state['PI_code']

    if PI_code:
        unique_pi_module_name = f'CFG_{PI_code}'
        unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

        start_year, end_year, Variable = UTILS.MAIN_FILTERS_streamlit_simple(ts_code,
            unique_pi_module_name,Years=True, Variable=True)

    return selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code

function_for_tab3()