import streamlit as st  # web development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
pd.set_option('mode.chained_assignment', None)
#import plotly.express as px  # interactive charts
import os
import importlib
from pathlib import Path
import sys
import io
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DUCK as CFG_DASHBOARD
from DASHBOARDS.UTILS import DASHBOARD_UTILS_DUCK as UTILS
import geopandas as gpd
import tempfile
import json
#import folium as f
#from folium import plugins
#import branca.colormap as cm
#import requests
import sys
import streamlit.components.v1 as components
#from streamlit_folium import st_folium

def get_env_var(var, env_name):
    """This function check if an env var is set and if the path of the env var
    exists.
    :param var: Value of the environment variable from os.getenv, if any
    :param env_name: Name of the environment variable
    :return: Path of the env var
    Called from set_path()
    """
    if not var:
        sys.exit(f'Variable {env_name} is not set')
    elif not os.path.isdir(var):
        sys.exit(f'Variable {env_name} is not a directory: {var}')
    else:
        print(f'{env_name} sets to {var} (exists).')
        return var

def set_base_path():
    CFG_DASHBOARD.post_process_folder = CFG_DASHBOARD.post_process_folder_name


set_base_path()


st.set_page_config(
    page_title='ISEE Dashboard',
    page_icon=':floppy_disk:',
    layout='wide',
    initial_sidebar_state="collapsed"

)

folder = CFG_DASHBOARD.post_process_folder
pis_code = CFG_DASHBOARD.pi_list
tss_code=CFG_DASHBOARD.ts_list

sct_poly = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.sct_poly_name)
sct_poly_country = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.sct_poly_country_name)
tiles_shp = os.path.join(CFG_DASHBOARD.shapefile_folder_name, CFG_DASHBOARD.tiles_shp_name)

pi_dct = {}
unit_dct = {}
for pi in pis_code:
    pi_module_name = f'CFG_{pi}'
    PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    pi_dct[pi] = PI_CFG.name
    unit_dct[pi] = PI_CFG.units

pis = [pi_dct[pi] for pi in pis_code]

ts_dct={'hist':'historical', 'sto':'stochastic', 'cc':'climate change'}

default_PI=next(iter(pi_dct.values()), None)
default_ts=next(iter(ts_dct.values()), None)

# State management
if 'PI_code' not in st.session_state:
    st.session_state['PI_code'] = pis_code[0]
    st.session_state['selected_pi'] = default_PI

if 'ts_code' not in st.session_state:
    st.session_state['ts_code'] = tss_code[0]
    st.session_state['selected_timeseries'] = default_ts

def update_PI_code():
    selected_pi_name = st.session_state['selected_pi']
    pi_code = [key for key, value in pi_dct.items() if value == selected_pi_name]
    #st.session_state['PI_code'] = selected_pi_name
    st.session_state['PI_code'] = pi_code[0]

def update_timeseries():
    selected_timeseries = st.session_state['timeseries']
    ts_code = [key for key, value in ts_dct.items() if value == selected_timeseries]
    #st.session_state['PI_code'] = selected_pi_name
    st.session_state['ts_code'] = ts_code[0]

st.title(CFG_DASHBOARD.title)

# st.markdown('Welcome to ISEE GLAM Dashboard \U0001F60A \n\r This interface allows you to interactively query ISEE results in order to compare Performance Indicator results under various water regulation plans \n\r First, please select a tab according to the way you want results to be displayed'
#          )

max_plans = CFG_DASHBOARD.maximum_plan_to_compare

if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'Bidon'

def switch_tab(tab_name):
    st.session_state['active_tab'] = tab_name

def switch_data(tile):
    st.session_state['data'] = tile

exec=False


st.session_state.gdf_grille_base = None
st.session_state.gdf_grille_plan = None
def function_for_tab1(exec):
    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
        with Col1:
            folder, LakeSL_prob_1D, selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts=render_column1()
            #full_min, full_max = UTILS.find_full_min_full_max(unique_pi_module_name, folder, PI_code, Variable)
        with Col2:

            st.write('👈 Set parameters with widgets on the left to display results accordingly')

            if no_plans_for_ts==True:
                st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

            else:
                UTILS.header(selected_pi, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values,
                             baseline_value, PI_code, unit_dct, var_direction, LakeSL_prob_1D)

                if LakeSL_prob_1D:
                    st.write(
                        ':red[For 1D PIs, It is not possible to have values compared to PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet! \n This is why delta values are all equal to 0 and why the Baseline values do not appear on the plot below.]')

                fig, df_PI_plans = UTILS.plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year,
                                            PI_code, unit_dct)

                csv_data=df_PI_plans.to_csv(index=False, sep=';')

                st.download_button(
                    label="Download displayed data in CSV format",
                    data=csv_data,
                    file_name="dataframe.csv",
                    mime="text/csv",
                    key='db_1'
                )

                st.plotly_chart(fig, use_container_width=True)

def function_for_tab2(exec):
    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
        with Col1:
            folder, LakeSL_prob_1D, selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts=render_column1()
            # full_min_diff, full_max_diff = UTILS.find_full_min_full_max_diff(unique_pi_module_name, folder, PI_code,
            #                                                                  Variable)
        with Col2:
            diff_type = st.selectbox("Select a type of difference to compute",
                                     [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'], key='select3')

            st.write('👈 Set parameters with widgets on the left to display results accordingly')

            if no_plans_for_ts==True:
                st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

            else:
                UTILS.header(selected_pi, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values,
                             baseline_value, PI_code, unit_dct, var_direction, LakeSL_prob_1D)

                if LakeSL_prob_1D:
                    st.write(':red[For 1D PIs, It is not possible to have values compared to PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')
                else:

                    fig2, df_PI_plans = UTILS.plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year,
                                                            PI_code, unit_dct, unique_pi_module_name, diff_type)

                    csv_data = df_PI_plans.to_csv(index=False, sep=';')

                    st.download_button(
                        label="Download displayed data in CSV format",
                        data=csv_data,
                        file_name="dataframe.csv",
                        mime="text/csv",
                        key='db_2'
                    )

                    st.plotly_chart(fig2, use_container_width=True)

def function_for_tab3(exec):
    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
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
                st.write(
                    ':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

            else:

                with candidate:
                    ze_plan2 = st.selectbox("Select a candidate plan to display", available_plans, key='ze_plan2', index=0)
                ze_plan_code = unique_PI_CFG.plan_dct[ze_plan2]
                var2 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]

                st.write('👈 Set other parameters with widgets on the left to display results accordingly')

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

                map_html = io.BytesIO()
                m.save(map_html, close_file=False)
                map_html.seek(0)
                st.download_button(
                    label="Download Map as HTML",
                    data=map_html.getvalue(),
                    file_name="map.html",
                    mime="text/html",
                    key='db_3'
                )

                col_map1, col_map2=st.columns(2)

                with col_map1:
                    shapefile_data = UTILS.save_gdf_to_zip(gdf_grille_base,
                                                           f'{PI_code}_{stat5}_{var}_{start_year}_{end_year}_{ts_code}_{baseline_code}.shp')
                    # Add the download button
                    st.download_button(
                        label="Download Baseline Map as shapefile",
                        data=shapefile_data,
                        file_name="Baseline_map.zip",
                        mime="application/zip",
                    )

                with col_map2:
                    shapefile_data = UTILS.save_gdf_to_zip(gdf_grille_plan,
                                                           f'{PI_code}_{stat5}_{var2}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}.shp')
                    # Add the download button
                    st.download_button(
                        label="Download Candidate Plan Map as shapefile",
                        data=shapefile_data,
                        file_name="Plan_map.zip",
                        mime="application/zip",
                    )

                UTILS.folium_static(m, 1200, 700)


def full_res_button(tile):
    if st.session_state.data==None:
        st.write('Click on a tile to see results in 10 x 10 meter resolution')
    else:
        st.write('this is a test')

def on_button_click():
    st.session_state.data = not st.session_state.data

def function_for_tab4(exec):
    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
        with Col1:
            selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Variable, ts_code=render_column1_simple()
            var3 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
            if unique_PI_CFG.var_agg_stat[var3][0]=='sum':
                stat3 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var3] + ['mean', 'min', 'max'], key='stat3', index=0)
            else:
                stat3 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var3] + ['min', 'max'], key='stat3', index=0)
            diff_type2 = st.selectbox("Select a type of difference to compute",
                                      [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'],
                                      key='diff_type2')

        with Col2:

            available_plans = unique_PI_CFG.plans_ts_dct[ts_code]
            baseline, candidate = st.columns(2)
            baselines=unique_PI_CFG.baseline_ts_dct[ts_code]
            if len(baselines)==0 or len(available_plans)==0:
                st.write(
                    ':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

            else:
                with baseline:
                    Baseline = st.selectbox("Select a reference plan to display", baselines)
                with candidate:
                    ze_plan = st.selectbox("Select a regulation plan to compare with reference plan", available_plans)

                baseline_code = unique_PI_CFG.baseline_dct[Baseline]
                ze_plan_code = unique_PI_CFG.plan_dct[ze_plan]
                start_year3 = start_year
                end_year3 = end_year
                if ts_code=='hist':
                    years_list=unique_PI_CFG.available_years_hist
                else:
                    years_list = unique_PI_CFG.available_years_future

                if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':

                    gdf_grille_base = UTILS.prep_for_prep_tiles_duckdb_lazy(tiles_shp, folder, PI_code, baseline_code,
                                                                years_list, stat3, var3,
                                                                unique_pi_module_name, start_year, end_year, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                    gdf_grille_plan = UTILS.prep_for_prep_tiles_duckdb_lazy(tiles_shp, folder, PI_code, ze_plan_code,
                                                                years_list, stat3, var3,
                                                                unique_pi_module_name, start_year, end_year, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                    division_col = 'tile'
                    gdf_both = gdf_grille_base.merge(gdf_grille_plan, on=['tile'], how='outer', suffixes=('_base', '_plan'))
                    gdf_both['geometry'] = np.where(gdf_both['geometry_base'] == None, gdf_both['geometry_plan'],
                                                    gdf_both['geometry_base'])
                    gdf_both = gdf_both[['tile', 'VAL_base', 'VAL_plan', 'geometry']]
                    gdf_both = gdf_both.fillna(0)
                    gdf_both['DIFF'] = gdf_both['VAL_plan'] - gdf_both['VAL_base']
                    gdf_both['DIFF_PROP'] = (
                            ((gdf_both['VAL_plan'] - gdf_both['VAL_base']) / gdf_both['VAL_base']) * 100).round(3)
                    gdf_both = gdf_both[['tile', 'DIFF', 'DIFF_PROP', 'geometry']]
                    gdf_both = gpd.GeoDataFrame(gdf_both, crs=4326, geometry=gdf_both['geometry'])

                    if diff_type2 == f'Values ({unit_dct[PI_code]})':
                        folium_map, empty_map = UTILS.create_folium_map(gdf_both, 'DIFF', 1200, 700, Variable,
                                                       unique_pi_module_name, division_col)
                    else:
                        folium_map, empty_map = UTILS.create_folium_map(gdf_both, 'DIFF_PROP', 1200, 700, Variable,
                                                       unique_pi_module_name, division_col)

                    st.write('👈 Set other parameters with widgets on the left to display results accordingly')

                    tile_selected = st.text_input(
                        'Type a tile number and press "Enter" to see results in full resolution (click on a tile to see its number) 👇', value=None)

                    dtypes = [type(element) for element in list(gdf_both['tile'])]

                    if tile_selected != None:

                        try:
                            tile_selected = int(tile_selected)
                            if tile_selected in list(gdf_both['tile']):
                                st.session_state.data = tile_selected
                            else:
                                st.write('Tile selected is not valid...')
                                st.session_state.data = None
                        except:
                            st.write('Tile selected is not valid...')
                            st.session_state.data = None
                    else:
                        st.session_state.data = None

                    pi_type=unique_PI_CFG.type
                    st.session_state.pi_type = pi_type
                    st.session_state.folder = folder
                    st.session_state.baseline_code = baseline_code
                    st.session_state.var = var3
                    st.session_state.years = years_list
                    st.session_state.ext = CFG_DASHBOARD.file_ext
                    st.session_state.start_year = start_year3
                    st.session_state.end_year = end_year3
                    st.session_state.stat = stat3
                    st.session_state.Variable = Variable
                    st.session_state.unique_pi_module_name = unique_pi_module_name
                    st.session_state.ze_plan_code = ze_plan_code
                    st.session_state.unit_dct = unit_dct
                    st.session_state.diff_type = diff_type2
                    st.session_state.PI_code = PI_code
                    st.session_state.ze_plan = ze_plan
                    st.session_state.Baseline = Baseline

                    if st.session_state.data:
                        st.link_button(
                            url=f'./Full_resolution_maps?pi_code={PI_code}&data={tile_selected}&folder={folder}&baseline_code={baseline_code}&var={var3}&years={years_list}&ext={CFG_DASHBOARD.file_ext}&start_year={start_year3}&end_year={end_year3}&stat={stat3}&Variable={Variable}&unique_pi_module_name={unique_pi_module_name}&ze_plan_code={ze_plan_code}&unit_dct={unit_dct}&diff_type={diff_type2}&PI_code={PI_code}&ze_plan={ze_plan}&Baseline={Baseline}&pi_type={pi_type}',
                            label=f"See tile {tile_selected} in full resolution"
                        )

                    if empty_map:
                        st.write(':red[There is no differences between those 2 plans with the selected parameters, hence no map can be displayed]')
                    else:
                        placeholder1 = st.empty()
                        with placeholder1.container():
                            st.subheader(
                               f'Difference (candidate minus reference plan) between the :blue[{stat3}] of :blue[{selected_pi} ({Variable}])  from :blue[{start_year} to {end_year}] in :blue[{diff_type2}]')
                        col_map_1, col_map_2=st.columns(2)
                        with col_map_1:
                            map_html = io.BytesIO()
                            folium_map.save(map_html, close_file=False)
                            map_html.seek(0)
                            st.download_button(
                                label="Download Map as HTML",
                                data=map_html.getvalue(),
                                file_name="map.html",
                                mime="text/html",
                                key='db_4'
                            )

                        with col_map_2:
                            shapefile_data = UTILS.save_gdf_to_zip(gdf_both,
                                                                   f'{PI_code}_{stat3}_{var3}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}_minus_{baseline_code}.shp')
                            # Add the download button
                            st.download_button(
                                label="Download map as shapefile",
                                data=shapefile_data,
                                file_name="difference_plan_minus_baseline.zip",
                                mime="application/zip",
                            )
                        click_data1 = UTILS.folium_static(folium_map, height=700, width=1200)

                else:
                    if unique_PI_CFG.divided_by_country:
                        sct_shp = sct_poly_country
                    else:
                        sct_shp = sct_poly

                    gdf_grille_base = UTILS.prep_for_prep_1d(ts_code, unique_PI_CFG.sect_dct, sct_shp, folder, PI_code,
                                                             baseline_code, years_list, stat3, var3,
                                                             unique_pi_module_name,
                                                             start_year3, end_year3, Baseline, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

                    gdf_grille_plan = UTILS.prep_for_prep_1d(ts_code, unique_PI_CFG.sect_dct, sct_shp, folder, PI_code, ze_plan_code,
                                                             years_list, stat3, var3,
                                                             unique_pi_module_name,
                                                             start_year3, end_year3, Baseline, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_urll)



                    division_col = 'SECTION'

                    gdf_grille_plan['DIFF'] = (gdf_grille_plan['VAL'] - gdf_grille_base['VAL']).round(3)

                    gdf_grille_plan['DIFF_PROP'] = (
                                ((gdf_grille_plan['VAL'] - gdf_grille_base['VAL']) / gdf_grille_base['VAL']) * 100).round(3)

                    if unique_PI_CFG.type=='1D' and 'PreProject' in Baseline:
                        gdf_grille_plan=gdf_grille_plan.loc[gdf_grille_plan['SECTION']!='Lake St.Lawrence']
                        st.write(':red[It is not possible to have values compared to PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')

                    if diff_type2 == f'Values ({unit_dct[PI_code]})':
                        data, empty_map = UTILS.create_folium_map(gdf_grille_plan, 'DIFF', 1200, 700, Variable,
                                                       unique_pi_module_name, division_col)

                    else:
                        data, empty_map = UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, Variable,
                                                       unique_pi_module_name, division_col)

                    if empty_map:
                        st.write(':red[There is no differences between those 2 plans with the selected parameters, hence no map can be displayed]')

                    else:
                        placeholder1 = st.empty()
                        with placeholder1.container():
                            st.subheader(
                                f'Difference (candidate minus reference plan) between the :blue[{stat3}] of :blue[{selected_pi} {Variable}]  from :blue[{start_year} to {end_year}] in :blue[{diff_type2}]')

                        col_map1, col_map2=st.columns(2)

                        with col_map1:
                            map_html = io.BytesIO()
                            data.save(map_html, close_file=False)
                            map_html.seek(0)
                            st.download_button(
                                label="Download Map as HTML",
                                data=map_html.getvalue(),
                                file_name="map.html",
                                mime="text/html",
                                key='db_5'
                            )

                        with col_map2:
                            shapefile_data = UTILS.save_gdf_to_zip(gdf_grille_plan,
                                                                   f'{PI_code}_{stat3}_{var3}_{start_year}_{end_year}_{ts_code}_{ze_plan_code}_minus_{baseline_code}.shp')

                            st.download_button(
                                label="Download map as shapefile",
                                data=shapefile_data,
                                file_name="difference_plan_minus_baseline.zip",
                                mime="application/zip",
                            )
                        click_data1=UTILS.folium_static(data, 1200, 700)

def render_column1():

    timeseries = st.selectbox("Select a supply", ts_dct.values(), key='timeseries',
                               on_change=update_timeseries)

    ts_code = st.session_state['ts_code']

    selected_pi=st.selectbox("Select a Performance Indicator", list(pi_dct.values()), key='selected_pi', on_change=update_PI_code)

    PI_code = st.session_state['PI_code']

    if PI_code:
        unique_pi_module_name = f'CFG_{PI_code}'
        unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

        start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, no_plans_for_ts = UTILS.MAIN_FILTERS_streamlit(ts_code,
            unique_pi_module_name, CFG_DASHBOARD,
            Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)

        LakeSL_prob_1D =False
        if unique_PI_CFG.type=='1D'and Region=='Lake St.Lawrence' and 'PreProject' in Baseline :
            LakeSL_prob_1D=True

        var_direction = unique_PI_CFG.var_direction[Variable]

        df_PI= UTILS.yearly_timeseries_data_prep(ts_code, unique_pi_module_name, folder, PI_code, plans_selected, Baseline, Region, start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D, CFG_DASHBOARD.sas_token, CFG_DASHBOARD.container_url)

        baseline_value, plan_values = UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI,
                                                                   unique_PI_CFG, LakeSL_prob_1D)

        list_plans = []
        for p in plans_selected:
            pp = unique_PI_CFG.plan_dct[p]
            list_plans.append(pp)
        list_plans.append(unique_PI_CFG.baseline_dct[Baseline])

    return folder, LakeSL_prob_1D, selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts

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

button_col1, button_col2, button_col3, button_col4  = st.columns(4)

with button_col1:
    if st.button('Timeseries'):
        switch_tab('Timeseries')

with button_col2:
    if st.button('Difference'):
        switch_tab('Difference')

with button_col3:
    if st.button('Dual Maps'):
        switch_tab('Dual Maps')

with button_col4:
    if st.button('Difference Maps'):
        switch_tab('Difference Maps')

if st.session_state['active_tab'] == 'Timeseries':
    function_for_tab1(exec=True)

elif st.session_state['active_tab'] == 'Difference':
    function_for_tab2(exec=True)

elif st.session_state['active_tab'] == 'Dual Maps':
    function_for_tab3(exec=True)

elif st.session_state['active_tab'] == 'Difference Maps':
    function_for_tab4(exec=True)

else:
    exec=False