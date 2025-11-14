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
from DASHBOARDS.UTILS.pages import Difference_maps_utils as UTILS
import geopandas as gpd

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

st.title('Difference maps 🌎')
st.subheader('Select what you want to see on the left, select which plan you want to compare and display the maps on the right.', divider="gray")

st.session_state.gdf_grille_plan = None

def function_for_tab4():
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
            print('Widget',stat)
        else:
            stat_list = unique_PI_CFG.var_agg_stat[var] + ['min', 'max']
            stat = st.selectbox("Select a way to aggregate values for the selected period",
                                stat_list, index=stat_list.index(st.session_state['selected_stat']),
                                key='_selected_stat', on_change=UTILS.update_session_state, args=('selected_stat', ))

        diff_type = st.selectbox("Select a type of difference to compute",
                                      [f'Values ({unique_PI_CFG.units})', 'Proportion of reference value (%)'],
                                      key='_diff_type', on_change=UTILS.update_session_state, args=('diff_type', ))

        if unique_PI_CFG.type in ['2D_tiled','2D_not_tiled']:
            division = 'TILE'
        else:
            division = 'SECTION'

        if 'df_PI_diffmaps' not in st.session_state:
            st.session_state['df_PI_diffmaps'] = UTILS.create_timeseries_database(f'test', PI_code, st.session_state['azure_container'],division)
        if (old_PI_code != PI_code):
            st.session_state['df_PI_diffmaps'] = UTILS.create_timeseries_database(f'test', PI_code, st.session_state['azure_container'],division)

        df_PI = st.session_state['df_PI_diffmaps']

    with Col2:
        st.subheader('**Plot**')
        # Compare with dual Maps
        available_plans = unique_PI_CFG.plans_ts_dct[ts_code]
        baseline, candidate = st.columns(2)
        baselines=unique_PI_CFG.baseline_ts_dct[ts_code]
        if len(baselines)==0 or len(available_plans)==0:
            st.write(
                ':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

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

            if ts_code=='hist':
                years_list=unique_PI_CFG.available_years_hist
            else:
                years_list = unique_PI_CFG.available_years_future

            if unique_PI_CFG.type in ['2D_tiled','2D_not_tiled']:

                gdf_grille_base = UTILS.prep_for_prep_tiles_parquet(tiles_shp, df_PI, baseline_code, stat, var,
                                                                        unique_PI_CFG, start_year, end_year, st.session_state['azure_container'])
                st.session_state['gdf_grille_base'] = gdf_grille_base

                gdf_grille_plan = UTILS.prep_for_prep_tiles_parquet(tiles_shp, df_PI, ze_plan_code, stat, var,
                                                                        unique_PI_CFG, start_year, end_year, st.session_state['azure_container'])

                # Compute difference between both plans
                division_col = 'TILE'
                gdf_both = gdf_grille_base.merge(gdf_grille_plan, on=['TILE'], how='outer', suffixes=('_base', '_plan'))
                gdf_both['geometry'] = np.where(gdf_both['geometry_base'] == None, gdf_both['geometry_plan'],
                                                gdf_both['geometry_base'])
                gdf_both = gdf_both[['TILE', 'VAL_base', 'VAL_plan', 'geometry']]
                gdf_both = gdf_both.fillna(0)

                if diff_type == f'Values ({unique_PI_CFG.units})':
                    gdf_both['DIFF'] = gdf_both['VAL_plan'] - gdf_both['VAL_base']
                    gdf_both = gdf_both[['TILE', 'DIFF', 'geometry']]
                    gdf_both = gpd.GeoDataFrame(gdf_both, crs=4326, geometry=gdf_both['geometry'])
                    folium_map, empty_map = UTILS.create_folium_map(gdf_both, 'DIFF', 1200, 700, Variable, unique_PI_CFG, division_col)
                else:
                    print(gdf_both[['VAL_plan','VAL_base']].tail(20))

                    gdf_both['DIFF_PROP'] = (
                        ((gdf_both['VAL_plan'] - gdf_both['VAL_base']) / gdf_both['VAL_base']) * 100).round(3)
                    gdf_both = gdf_both[['TILE', 'DIFF_PROP', 'geometry']]
                    gdf_both = gpd.GeoDataFrame(gdf_both, crs=4326, geometry=gdf_both['geometry'])
                    # remove infinite difference (when division per 0)
                    gdf_both['DIFF_PROP'] = gdf_both['DIFF_PROP'].replace([np.inf, -np.inf], np.nan)
                    gdf_both.dropna(subset='DIFF_PROP', inplace=True)
                    folium_map, empty_map = UTILS.create_folium_map(gdf_both, 'DIFF_PROP', 1200, 700, Variable,unique_PI_CFG, division_col)

                if empty_map:
                    st.write(':red[There is no differences between those 2 plans with the selected parameters, hence no map can be displayed]')
                else:
                    placeholder1 = st.empty()
                    with placeholder1.container():
                        st.subheader(
                           f'Difference (candidate minus reference plan) between the :blue[{stat}] of :blue[{unique_PI_CFG.name} ({Variable}])  from :blue[{start_year} to {end_year}] in :blue[{diff_type}]')

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


                division_col = 'SECTION'

                if unique_PI_CFG.type=='1D' and 'PreProject' in Baseline:
                    gdf_grille_plan=gdf_grille_plan.loc[gdf_grille_plan['SECTION']!='Lake St.Lawrence']
                    st.write(':red[It is not possible to have values compared to PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')

                if diff_type == f'Values ({unique_PI_CFG.units})':
                    gdf_grille_plan['DIFF'] = (gdf_grille_plan['VAL'] - gdf_grille_base['VAL']).round(3)
                    gdf_grille_plan.dropna(inplace=True)
                    folium_map, empty_map = UTILS.create_folium_map(gdf_grille_plan, 'DIFF', 1200, 700, Variable,
                                                   unique_PI_CFG, division_col)

                else:
                    gdf_grille_plan['DIFF_PROP'] = (
                                ((gdf_grille_plan['VAL'] - gdf_grille_base['VAL']) / gdf_grille_base['VAL']) * 100).round(3)
                    gdf_grille_plan.dropna(inplace=True)
                    folium_map, empty_map = UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, Variable,
                                                   unique_PI_CFG, division_col)
                gdf_both = gdf_grille_plan

                if empty_map:
                    st.write(':red[There is no differences between those 2 plans with the selected parameters, hence no map can be displayed]')

                else:
                    placeholder1 = st.empty()
                    with placeholder1.container():
                        st.subheader(
                            f'Difference (candidate minus reference plan) between the :blue[{stat}] of :blue[{unique_PI_CFG.name} {Variable}]  from :blue[{start_year} to {end_year}] in :blue[{diff_type}]')

            if not empty_map:
                col_shape, col_html=st.columns(2,gap='small',width=450)

                with col_shape:
                    shape_button = st.container()

                with col_html:
                    html_button = st.container()

                UTILS.folium_static(folium_map, height=700, width=1200)

                with shape_button:
                    st.download_button(
                                label="Download map as shapefile",
                                data=prepare_shapefile(gdf_both,f'{PI_code}_{stat}_{var}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}_minus_{baseline_code}.shp'),
                                file_name="difference_plan_minus_baseline.zip",
                                mime="application/zip")
                with html_button:
                    st.download_button(
                            label="Download Map as HTML",
                            data=prepare_html(folium_map),
                            file_name="map.html",
                            mime="text/html",
                            key='db_4', type='primary')

                with Col1:
                    if unique_PI_CFG.type in ['2D_tiled','2D_not_tiled']:
                        st.divider()
                        st.subheader("Full resolution map")
                        st.write('Choose a tile to see it in full resolution')
                        # Show a full resolution map
                        tile_selected = st.selectbox(label='Choose a tile',label_visibility='collapsed',width=100,
                                                     options=np.sort(gdf_both['TILE'].astype(int).unique()),
                                                     key='_selected_tile',on_change=UTILS.update_session_state, args=('selected_tile', ))

                        # Est-ce que tout ça c'est nécessaire?
                        st.session_state.data = tile_selected
                        pi_type=unique_PI_CFG.type
                        st.session_state.pi_type = pi_type
                        st.session_state.folder = folder
                        st.session_state.baseline_code = baseline_code
                        st.session_state.var = var
                        st.session_state.years = years_list
                        st.session_state.ext = CFG_DASHBOARD.file_ext
                        st.session_state.start_year = start_year
                        st.session_state.end_year = end_year
                        st.session_state.stat = stat
                        st.session_state.Variable = Variable
                        st.session_state.unique_pi_module_name = unique_PI_CFG.pi_code
                        st.session_state.ze_plan_code = ze_plan_code
                        st.session_state.unit = unique_PI_CFG.units
                        st.session_state.diff_type = diff_type
                        st.session_state.PI_code = PI_code
                        st.session_state.ze_plan = ze_plan
                        st.session_state.Baseline = Baseline

                        st.link_button(url=f'./Full_resolution_maps_🔍?pi_code={PI_code}&data={tile_selected}&folder={folder}&baseline_code={baseline_code}&var={var}&years={years_list}&ext={CFG_DASHBOARD.file_ext}&start_year={start_year}&end_year={end_year}&stat={stat}&Variable={Variable}&unique_pi_module_name={unique_PI_CFG.pi_code}&ze_plan_code={ze_plan_code}&unit={unique_PI_CFG.units}&diff_type={diff_type}&PI_code={PI_code}&ze_plan={ze_plan}&Baseline={Baseline}&pi_type={pi_type}',
                                       label=f"👉 See tile {tile_selected} in full resolution",
                                       type='primary',width='stretch')


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
    function_for_tab4()
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