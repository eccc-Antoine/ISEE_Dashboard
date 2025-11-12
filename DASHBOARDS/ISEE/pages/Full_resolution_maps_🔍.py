import streamlit as st
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import os
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
import CFG_ISEE_DUCK as CFG_DASHBOARD
from DASHBOARDS.UTILS.pages import Full_resolution_maps_utils as UTILS
import tempfile
from datetime import datetime as dt
from azure.storage.blob import BlobServiceClient

start = dt.now()

st.set_page_config(
    page_title='ISEE Dashboard',
    page_icon='🏞️',
    layout='wide',
    initial_sidebar_state="collapsed")

folder = CFG_DASHBOARD.post_process_folder
pis_code = CFG_DASHBOARD.pi_list # PI list
tss_code=CFG_DASHBOARD.ts_list # Timeserie list

# Thoses files are in \\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\shapefiles\
sct_poly = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.sct_poly_name)
sct_poly_country = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.sct_poly_country_name)
tiles_shp = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.tiles_shp_name)

# Import PI configuration
# Remove 1D PI for this page
pis_code = [pi for pi in pis_code if '1D' not in pi]
pi_dct = {}
for pi in pis_code:
    if '1D' not in pis_code:
        pi_module_name = f'CFG_{pi}'
        PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        pi_dct[pi] = PI_CFG.name
del PI_CFG

# Pretty name of pi
pis = list(pi_dct.values())

ts_dct={'hist':'historical', 'sto':'stochastic', 'cc':'climate change'}

default_PI=next(iter(pi_dct.values()), None)
default_ts=next(iter(ts_dct.values()), None)

# Pour la carte
mapbox_token='pk.eyJ1IjoidG9ueW1hcmFuZGExOTg1IiwiYSI6ImNsM3cwYm8zeDAzNHAzY3FxcWV3ZXJkbWEifQ.5rgErxAFf7_k0Kn0mz3RdA'
style_url='mapbox://styles/tonymaranda1985/clmhwft2i03rs01ph9z2kbbos'

container_url = 'https://eccciseedashboardst.blob.core.windows.net/dukc-db'
sas_token = 'sp=r&st=2025-09-23T17:49:14Z&se=2026-01-01T03:04:14Z&spr=https&sv=2024-11-04&sr=c&sig=iDZm15DwnTl%2BHGsamuEu0atH%2BiIULEyNtew8rCtUkIU%3D'

# initialize request
qp = st.query_params

st.cache_data.clear()
st.cache_resource.clear()

if 'PI_code' not in st.session_state:
    if 'pi_code' in qp:
        st.session_state['PI_code'] = qp['pi_code']
        st.session_state['selected_pi'] = pi_dct[qp['pi_code']]
    else:
        st.session_state['PI_code'] = pis_code[0]
        st.session_state['selected_pi'] = default_PI

if '1D' in st.session_state['PI_code']:
    st.session_state['PI_code'] = pis_code[0]
    st.session_state['selected_pi'] = default_PI
    UTILS.initialize_session_state()

if 'unique_PI_CFG' not in st.session_state:
    PI_code = st.session_state['PI_code']
    st.session_state['unique_PI_CFG'] = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{PI_code}')

if 'ts_code' not in st.session_state:
    if 'pi_code' in qp:
        if qp['ze_plan_code'] in st.session_state['unique_PI_CFG'].plans_ts_dct['hist']:
            st.session_state['ts_code'] = 'hist'
        elif qp['ze_plan_code'] in st.session_state['unique_PI_CFG'].plans_ts_dct['sto']:
            st.session_state['ts_code'] = 'sto'
        else:
            st.session_state['ts_code'] = 'cc'
        st.session_state['selected_timeseries'] = ts_dct[st.session_state['ts_code']]
    else:
        st.session_state['ts_code'] = tss_code[0]
        st.session_state['selected_timeseries'] = default_ts

if 'azure_container' not in st.session_state:
    # connect to Azur blob storage
    blob_service_client = BlobServiceClient(CFG_DASHBOARD.azure_url, credential = CFG_DASHBOARD.access_key)
    container = blob_service_client.get_container_client('dukc-db')
    st.session_state['azure_container'] = container
    UTILS.initialize_session_state()

if len(qp) > 0:

    st.session_state['Baseline'] = qp['Baseline']
    st.session_state['ze_plan'] = qp['ze_plan']
    st.session_state['selected_tile'] = int(qp['data'])
    st.session_state['selected_variable'] = st.session_state['unique_PI_CFG'].dct_var[qp['var']]
    st.session_state['selected_years'] = [int(qp['start_year']),int(qp['end_year'])]
    st.session_state['selected_stat'] = qp['stat']
    st.session_state['diff_type'] = qp['diff_type']

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

st.title('Full resolution maps 🔍')
st.subheader('Select what you want to see on the left, select which plans you want to compare and display one tile in full resolution on the right.', divider="gray")

def function_for_tab5():
    Col1, Col2 = st.columns([0.2, 0.8], gap='large')
    with Col1:
        st.subheader('**Parameters**')
        old_PI_code, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code=render_column1_tile()
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

        diff_type = st.selectbox("Select a type of difference to compute",
                                      [f'Values ({unique_PI_CFG.units})', 'Proportion of reference value (%)'],
                                      key='_diff_type', on_change=UTILS.update_session_state, args=('diff_type', ))


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

            # Find which tile is available
            tiles_list = possible_tiles(baseline_code,ze_plan_code,PI_code,folder).tolist()
            # Happens when we change the PI or the ts_code
            if st.session_state['selected_tile'] == None:
                st.session_state['selected_tile'] = tiles_list[0]
            st.write('Choose a tile to see it in full resolution')
            col_select, col_but, col_spin = st.columns([0.2,0.21,0.59],gap='small',vertical_alignment='center')
            with col_select:
                # For the tile, add available tiles per PI in cfg
                tile_selected = st.selectbox(label='Choose a tile',label_visibility='collapsed',
                                             options=tiles_list,index=tiles_list.index(st.session_state['selected_tile']),
                                             key='_selected_tile',on_change=UTILS.update_session_state, args=('selected_tile', ))
            with col_but:
                plot_map = st.button(label='Click here to plot the map 🗺️',type='primary')
            with col_spin:
                spinner_container = st.container()
        map_container = st.container()
        if plot_map or len(qp)!=0:
            # add progress bar
            with spinner_container:
                with st.spinner(text='Importing data...'):
                    print('IMPORT DATA AND PLOT MAP')

                    df_base = UTILS.read_all_files_in_tile(st.session_state['azure_container'], st.session_state['unique_PI_CFG'],
                                                        baseline_code, st.session_state['ts_code'], tile_selected, var, folder)

                    df_base = UTILS.prep_data_map(df_base, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, 'CFG_'+unique_PI_CFG.pi_code)
                    df_base = df_base.sort_values(by='LAT')

                    # Plan to compare
                    df_plan = UTILS.read_all_files_in_tile(st.session_state['azure_container'], st.session_state['unique_PI_CFG'],
                                                        ze_plan_code, st.session_state['ts_code'], tile_selected, var, folder)
            with spinner_container:
                with st.spinner(text='Plotting map...'):
                    df_plan=UTILS.prep_data_map(df_plan, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, 'CFG_'+unique_PI_CFG.pi_code)
                    df_both=df_base.merge(df_plan, on=['PT_ID'], how='outer', suffixes=('_base', '_plan'))
                    df_both=df_both.fillna(0)

                    if diff_type==f'Values ({unique_PI_CFG.units})':
                        df_both['diff']=df_both[f'{Variable}_plan']-df_both[f'{Variable}_base']
                    else:
                        df_both['diff']=((df_both[f'{Variable}_plan']-df_both[f'{Variable}_base'])/df_both[f'{Variable}_base'])*100

                    df_both['diff']=df_both['diff'].round(3)
                    df_both.dropna(subset = ['diff'], inplace=True)

                    df_both=df_both.loc[df_both['diff']!=0]

                    lon_cols=[col for col in list(df_both) if 'LON' in col]
                    lon_col=lon_cols[0]

                    lat_cols=[col for col in list(df_both) if 'LAT' in col]
                    lat_col=lat_cols[0]

                    df_both['LAT']=np.where(df_both['LAT_base'] == 0, df_both['LAT_plan'], df_both['LAT_base'])
                    df_both['LON']=np.where(df_both['LON_base'] == 0, df_both['LON_plan'], df_both['LON_base'])

                    fig=UTILS.plot_map_plotly(Variable, df_both, 'LON', 'LAT', 'CFG_'+unique_PI_CFG.pi_code, 'diff', mapbox_token, style_url)

                    with map_container:
                        if fig =='empty':
                            st.write('There is no difference between those two plans according to the widget parameters. Please, change parameters on the previous page...')

                        else:
                            st.write('👇 Download map as')
                            col_shape, col_html=st.columns(2,gap=None,width=200)

                            with col_shape:
                                shape_button = st.empty()
                                with shape_button:
                                    st.button('Shapefile',disabled=True)

                            with col_html:
                                html_button = st.empty()
                                with html_button:
                                    st.button('HTML',disabled=True,type='primary')
                            st.plotly_chart(fig, use_container_width=True)
            if fig != 'empty':
                with spinner_container:
                    with st.spinner('Preparing files to download...'):
                        with html_button:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                                fig.write_html(tmp_file.name)
                                tmp_file.seek(0)
                                html_button.empty()
                                st.download_button(
                                    label="HTML",
                                    data=tmp_file.read(),
                                    file_name="map.html",
                                    mime="text/html",
                                    type='primary'
                                )

                        with shape_button:

                            gdf=UTILS.df_2_gdf(df_both, 'LON', 'LAT', 4326)
                            shapefile_data = UTILS.save_gdf_to_zip(gdf,
                                                                f'{PI_code}_{stat}_{var}_{start_year}_{end_year}_{ze_plan_code}_minus_{baseline_code}.shp')
                            shape_button.empty()
                            st.download_button(
                                label="Shapefile",
                                data=shapefile_data,
                                file_name="difference_plan_minus_baseline.zip",
                                mime="application/zip",
                            )


def render_column1_tile():

    old_ts_code = st.session_state['ts_code']
    ts_list = list(ts_dct.values())
    st.selectbox("Select a supply", ts_list,
                 index=ts_list.index(ts_dct[st.session_state['ts_code']]), key='timeseries')
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

    start_year, end_year, Variable = UTILS.MAIN_FILTERS_streamlit_with_cache(ts_code,
            unique_PI_CFG, Years=True, Variable=True)

    return old_PI_code, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code

def possible_tiles(baseline_code, ze_plan_code, PI_code, folder):
    container = st.session_state['azure_container']
    pi_folder = os.path.join(folder,PI_code,'YEAR\PT_ID').replace('\\','/')
    # Baseline tiles
    baseline_parquets = container.list_blob_names(name_starts_with = os.path.join(pi_folder,baseline_code).replace('\\','/'))
    baseline_parquets = [f.split('/')[-1] for f in baseline_parquets]
    baseline_tiles = [int(f.split('_')[-3]) for f in baseline_parquets]
    # Plan tiles
    ze_plan_parquets = container.list_blob_names(name_starts_with = os.path.join(pi_folder,ze_plan_code).replace('\\','/'))
    ze_plan_parquets = [f.split('/')[-1] for f in ze_plan_parquets]
    ze_plan_tiles = [int(f.split('_')[-3]) for f in ze_plan_parquets]
    return(np.intersect1d(baseline_tiles,ze_plan_tiles))

function_for_tab5()
print('Execution time :', dt.now()-start)
print('----------------------------END----------------------------')

if len(qp) != 0:
    st.query_params.clear()