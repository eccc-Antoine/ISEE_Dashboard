import streamlit as st  # web development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation

# pd.options.mode.copy_on_write = True
pd.set_option('mode.chained_assignment', None)
import plotly.express as px  # interactive charts
import os
import importlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DASH as CFG_DASHBOARD
from DASHBOARDS.UTILS import DASHBOARDS_UTILS as UTILS
import geopandas as gpd
import json
import folium as f
from folium import plugins
import branca.colormap as cm
import requests
import sys
import streamlit.components.v1 as components
from streamlit_folium import st_folium

st.set_page_config(
    page_title='ISEE Dashboard',
    page_icon=':floppy_disk:',
    layout='wide'
)

folder = CFG_DASHBOARD.post_process_folder
pis_code = CFG_DASHBOARD.pi_list

pi_dct = {}
unit_dct = {}
for pi in pis_code:
    pi_module_name = f'CFG_{pi}'
    PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    pi_dct[pi] = PI_CFG.name
    unit_dct[pi] = PI_CFG.units

pis = [pi_dct[pi] for pi in pis_code]

default_PI=pis_code[0]
# State management
if 'PI_code' not in st.session_state:
    st.session_state['PI_code'] = pis_code[0]
    st.session_state['selected_pi'] = default_PI


def update_PI_code():
    selected_pi_name = st.session_state['selected_pi']
    print(selected_pi_name)
    #st.session_state['PI_code'] = next(pi for pi, name in pi_dct.items() if name == selected_pi_name)
    st.session_state['PI_code'] = selected_pi_name


st.title(CFG_DASHBOARD.title)

#Col1, Col2 = st.columns([0.2, 0.8])

max_plans = CFG_DASHBOARD.maximum_plan_to_compare

if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'Bidon'

def switch_tab(tab_name):
    st.session_state['active_tab'] = tab_name

def switch_data(tile):
    st.session_state['data'] = tile

exec=False
def function_for_tab1(exec):

    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
        with Col1:
            unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans=render_column1()

        with Col2:

            st.write('👈 Set parameters with widgets on the left to display results accordingly')

            UTILS.header(Stats, PI_code, start_year, end_year, Region, plans_selected, Baseline, max_plans, plan_values,
                         baseline_value, PI_code, unit_dct, var_direction)

            fig = UTILS.plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year,
                                        PI_code, unit_dct)
            st.plotly_chart(fig, use_container_width=True)

def function_for_tab2(exec):
    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
        with Col1:
            unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans=render_column1()

        with Col2:
            diff_type = st.selectbox("Select a type of difference to compute",
                                     [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'], key='select3')

            st.write('👈 Set parameters with widgets on the left to display results accordingly')

            UTILS.header(Stats, PI_code, start_year, end_year, Region, plans_selected, Baseline, max_plans, plan_values,
                         baseline_value, PI_code, unit_dct, var_direction)
            fig2 = UTILS.plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year,
                                                    PI_code, unit_dct, unique_pi_module_name, diff_type)
            st.plotly_chart(fig2, use_container_width=True)


def function_for_tab3(exec):
    if exec:
        Col1, Col2 = st.columns([0.2, 0.8])
        with Col1:
            unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Variable=render_column1_simple()
            var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
            print(unique_PI_CFG.var_agg_stat[var])
            if unique_PI_CFG.var_agg_stat[var][0] =='sum':
                stat5 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var] + ['mean', 'min', 'max'], key='stat5', index=0)
            else:
                stat5 = st.selectbox("Select a way to aggregate values for the selected period",
                                     unique_PI_CFG.var_agg_stat[var] + ['min', 'max'], key='stat5', index=0)

        with Col2:

            baseline, candidate = st.columns(2)
            baselines = list(unique_PI_CFG.baseline_dct.keys())
            with baseline:
                Baseline2 = st.selectbox("Select a reference plan to display", baselines)

            baseline_code = unique_PI_CFG.baseline_dct[Baseline2]

            available_plans = {i for i in unique_PI_CFG.plan_dct if
                               unique_PI_CFG.plan_dct[i] in unique_PI_CFG.available_plans}
            with candidate:
                ze_plan2 = st.selectbox("Select a candidate plan to display", available_plans, key='ze_plan2', index=0)
            ze_plan_code = unique_PI_CFG.plan_dct[ze_plan2]
            var2 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]

            st.write('👈 Set other parameters with widgets on the left to display results accordingly')

            if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':

                gdf_grille_base = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, baseline_code,
                                                            unique_PI_CFG.available_years, stat5, var,
                                                            unique_pi_module_name, start_year, end_year)
                gdf_grille_plan = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, ze_plan_code,
                                                            unique_PI_CFG.available_years, stat5, var,
                                                            unique_pi_module_name, start_year, end_year)

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', 700, 700, Variable, 'compare',
                                                 unique_pi_module_name, unit_dct[PI_code], 'tile')

            else:

                if unique_PI_CFG.divided_by_country:
                    sct_shp = CFG_DASHBOARD.sct_poly_country
                else:
                    sct_shp = CFG_DASHBOARD.sct_poly

                gdf_grille_base = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder,
                                                         PI_code, baseline_code, unique_PI_CFG.available_years, stat5,
                                                         var, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
                                                         start_year, end_year, Baseline)

                gdf_grille_plan = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder,
                                                         PI_code, ze_plan_code, unique_PI_CFG.available_years, stat5,
                                                         var2, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
                                                         start_year, end_year, Baseline)

                m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', 1200, 700, Variable,
                                                 'compare', unique_pi_module_name, unit_dct[PI_code], 'SECTION')

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
            unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Variable=render_column1_simple()
            var3 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
            stat3 = st.selectbox("Select a way to aggregate values for the selected period",
                                 unique_PI_CFG.var_agg_stat[var3] + ['Min', 'Max'], key='stat3', index=0)
            diff_type2 = st.selectbox("Select a type of difference to compute",
                                      [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'],
                                      key='diff_type2')

        with Col2:
            available_plans = {i for i in unique_PI_CFG.plan_dct if
                               unique_PI_CFG.plan_dct[i] in unique_PI_CFG.available_plans}

            baseline, candidate = st.columns(2)
            baselines = list(unique_PI_CFG.baseline_dct.keys())
            with baseline:
                Baseline = st.selectbox("Select a reference plan to display", baselines)

            with candidate:
                ze_plan = st.selectbox("Select a regulation plan to compare with reference plan", available_plans)

            baseline_code = unique_PI_CFG.baseline_dct[Baseline]
            ze_plan_code = unique_PI_CFG.plan_dct[ze_plan]

            start_year3 = start_year
            end_year3 = end_year

            if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':



                # def link_button(PI_code, tile_selected, folder):
                #     if not tile_selected:
                #         st.link_button(label='Need to select a tile first', disabled=True)
                #     else:
                #         st.link_button(
                #             url=f'./test?pi_code={PI_code}&data={tile_selected}&folder={folder}&baseline_code={baseline_code}&var={var3}&years={unique_PI_CFG.available_years}&ext={CFG_DASHBOARD.file_ext}&start_year={start_year3}&end_year={end_year3}&stat={stat3}&Variable={Variable}&unique_pi_module_name={unique_pi_module_name}&ze_plan_code={ze_plan_code}&unit_dct={unit_dct}&diff_type={diff_type2}&PI_code={PI_code}&ze_plan={ze_plan}&Baseline={Baseline}',
                #             label=f"See tile {tile} in full resolution"
                #         )

                # if 'data' not in st.session_state:
                #     st.session_state.data = False
                #
                # if not st.session_state.data:
                #     st.write('Click on a tile to see results in 10 x 10 meter resolution')
                #
                # else:
                #     st.write('this is a test')
                #tile=st.session_state.data
                #full_res_button(tile)

                gdf_grille_base = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, ze_plan_code,
                                                            unique_PI_CFG.available_years, stat3, var3,
                                                            unique_pi_module_name, start_year, end_year)

                gdf_grille_plan = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, baseline_code,
                                                            unique_PI_CFG.available_years, stat3, var3,
                                                            unique_pi_module_name, start_year, end_year)

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
                    folium_map = UTILS.create_folium_map(gdf_both, 'DIFF', 1200, 700, Variable, 'diff',
                                                   unique_pi_module_name, unit_dct[PI_code], division_col)
                else:
                    folium_map = UTILS.create_folium_map(gdf_both, 'DIFF_PROP', 1200, 700, Variable, 'diff',
                                                   unique_pi_module_name, unit_dct[PI_code], division_col)

                st.write('👈 Set other parameters with widgets on the left to display results accordingly')

                tile_selected = st.text_input(
                    "Enter a tile number to see its results in full resolution (click on a tile to see its number) 👇", value=None)

                print(list(gdf_both['tile']))
                dtypes = [type(element) for element in list(gdf_both['tile'])]
                print(dtypes)

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


                #click_data = st_folium(folium_map, height=1200, width=1200)



                # print(click_data)
                # print(click_data1)
                #
                # tile = click_data['last_object_clicked_popup']
                # if tile != None:
                #     tile = str(tile)
                #     tile = tile.replace('tile', '')
                #     tile = tile.replace(' ', '')
                #     tile = tile.replace('\n', '')
                #     tile = int(tile)
                # else:
                #     tile = None
                # switch_data(tile)

                #st.session_state.data = tile
                #st.session_state.PI = PI_code
                st.session_state.folder = folder
                st.session_state.baseline_code = baseline_code
                st.session_state.var = var3
                st.session_state.years = unique_PI_CFG.available_years
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

                # for item in st.session_state.items():
                #     print(item)

                if st.session_state.data:
                    st.link_button(
                        url=f'./Full_resolution_maps?pi_code={PI_code}&data={tile_selected}&folder={folder}&baseline_code={baseline_code}&var={var3}&years={unique_PI_CFG.available_years}&ext={CFG_DASHBOARD.file_ext}&start_year={start_year3}&end_year={end_year3}&stat={stat3}&Variable={Variable}&unique_pi_module_name={unique_pi_module_name}&ze_plan_code={ze_plan_code}&unit_dct={unit_dct}&diff_type={diff_type2}&PI_code={PI_code}&ze_plan={ze_plan}&Baseline={Baseline}',
                        label=f"See tile {tile_selected} in full resolution"
                    )

                click_data1 = UTILS.folium_static(folium_map, height=700, width=1200)

                # def navigate_to(new_page):
                #     st.query_params(page=f'./test?pi_code={PI_code}&data={tile_selected}&folder={folder}&baseline_code={baseline_code}&var={var3}&years={unique_PI_CFG.available_years}&ext={CFG_DASHBOARD.file_ext}&start_year={start_year3}&end_year={end_year3}&stat={stat3}&Variable={Variable}&unique_pi_module_name={unique_pi_module_name}&ze_plan_code={ze_plan_code}&unit_dct={unit_dct}&diff_type={diff_type2}&PI_code={PI_code}&ze_plan={ze_plan}&Baseline={Baseline}')
                #
                # if tile_selected:
                #     navigate_to('test')

            else:
                if unique_PI_CFG.divided_by_country:
                    sct_shp = CFG_DASHBOARD.sct_poly_country
                else:
                    sct_shp = CFG_DASHBOARD.sct_poly

                gdf_grille_base = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder, PI_code,
                                                         baseline_code, unique_PI_CFG.available_years, stat3, var3,
                                                         unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
                                                         start_year3, end_year3, Baseline)

                gdf_grille_plan = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder, PI_code, ze_plan_code,
                                                         unique_PI_CFG.available_years, stat3, var3,
                                                         unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
                                                         start_year3, end_year3, Baseline)

                division_col = 'SECTION'

                gdf_grille_plan['DIFF'] = (gdf_grille_plan['VAL'] - gdf_grille_base['VAL']).round(3)

                gdf_grille_plan['DIFF_PROP'] = (
                            ((gdf_grille_plan['VAL'] - gdf_grille_base['VAL']) / gdf_grille_base['VAL']) * 100).round(3)

                if diff_type2 == f'Values ({unit_dct[PI_code]})':
                    data = UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, Variable, 'diff',
                                                   unique_pi_module_name, unit_dct[PI_code], division_col)

                else:
                    data = UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, Variable, 'diff',
                                                   unique_pi_module_name, unit_dct[PI_code], division_col)


def render_column1():

    selected_pi=st.selectbox("Select a Performance Indicator", list(pi_dct.keys()), key='selected_pi', on_change=update_PI_code)

    PI_code = st.session_state['PI_code']

    #disabled = st.session_state.active_tab == "Dual Maps"

    if PI_code:
        unique_pi_module_name = f'CFG_{PI_code}'
        unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

        start_year, end_year, Region, plans_selected, Baseline, Stats, Variable = UTILS.MAIN_FILTERS_streamlit(
            unique_pi_module_name, CFG_DASHBOARD,
            Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)

        var_direction = unique_PI_CFG.var_direction[Variable]

        df_PI = UTILS.yearly_timeseries_data_prep(unique_pi_module_name, folder, PI_code, plans_selected, Baseline, Region,
                                                  start_year, end_year, Variable, CFG_DASHBOARD)

        baseline_value, plan_values = UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI,
                                                                   unique_PI_CFG)

        list_plans = []
        for p in plans_selected:
            pp = unique_PI_CFG.plan_dct[p]
            list_plans.append(pp)
        list_plans.append(unique_PI_CFG.baseline_dct[Baseline])

    return unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans

def render_column1_simple():
    selected_pi=st.selectbox("Select a Performance Indicator", list(pi_dct.keys()), key='selected_pi', on_change=update_PI_code)

    PI_code = st.session_state['PI_code']

    #disabled = st.session_state.active_tab == "Dual Maps"

    if PI_code:
        unique_pi_module_name = f'CFG_{PI_code}'
        unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

        start_year, end_year, Variable = UTILS.MAIN_FILTERS_streamlit_simple(
            unique_pi_module_name, CFG_DASHBOARD,
            Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)


    return unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Variable


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



#     with tab2:
#         active_tab = "Tab 2"
#         function_for_tab2()
#
#     with tab3:
#         active_tab = "Tab 3"
#         function_for_tab3()
#
# if active_tab == "Tab 2":
#     function_for_tab2()
#
# elif active_tab == "Tab 3":
#     function_for_tab3()

        #
        # with tab4:
        #
        #     baselines = list(unique_PI_CFG.baseline_dct.keys())
        #     Baseline2 = st.selectbox("Select a reference plan to display.", baselines)
        #
        #     baseline_code = unique_PI_CFG.baseline_dct[Baseline2]
        #     var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
        #     stat5 = st.selectbox("Select a way to aggregate values for the selected period..",
        #                          unique_PI_CFG.var_agg_stat[var] + ['Min', 'Max'], key='stat5', index=0)
        #
        #     available_plans = {i for i in unique_PI_CFG.plan_dct if
        #                        unique_PI_CFG.plan_dct[i] in unique_PI_CFG.available_plans}
        #     ze_plan2 = st.selectbox("Select a candidate plan to display..", available_plans, key='ze_plan2', index=0)
        #     ze_plan_code = unique_PI_CFG.plan_dct[ze_plan2]
        #     var2 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
        #
        #     if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':
        #         gdf_grille_base = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, baseline_code,
        #                                                     unique_PI_CFG.available_years, stat5, var,
        #                                                     unique_pi_module_name, start_year, end_year)
        #         gdf_grille_plan = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, ze_plan_code,
        #                                                     unique_PI_CFG.available_years, stat5, var,
        #                                                     unique_pi_module_name, start_year, end_year)
        #
        #         m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', 700, 700, Variable, 'compare',
        #                                          unique_pi_module_name, unit_dct[PI_code], 'tile')
        #
        #     else:
        #
        #         if unique_PI_CFG.divided_by_country:
        #             sct_shp = CFG_DASHBOARD.sct_poly_country
        #         else:
        #             sct_shp = CFG_DASHBOARD.sct_poly
        #
        #         gdf_grille_base = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder,
        #                                                  PI_code, baseline_code, unique_PI_CFG.available_years, stat5,
        #                                                  var, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
        #                                                  start_year, end_year, Baseline)
        #
        #         gdf_grille_plan = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder,
        #                                                  PI_code, ze_plan_code, unique_PI_CFG.available_years, stat5,
        #                                                  var2, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
        #                                                  start_year, end_year, Baseline)
        #
        #         m = UTILS.create_folium_dual_map(gdf_grille_base, gdf_grille_plan, 'VAL', 1200, 700, Variable,
        #                                          'compare', unique_pi_module_name, unit_dct[PI_code], 'SECTION')
        #
        #     UTILS.folium_static(m, 1200, 700)
        #
        # with tab5:
        #     ze_plan = st.selectbox("Select a regulation plan to compare with reference plan", available_plans)
        #     baseline_code = unique_PI_CFG.baseline_dct[Baseline]
        #     ze_plan_code = unique_PI_CFG.plan_dct[ze_plan]
        #     var3 = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
        #     stat3 = st.selectbox("Select a way to aggregate values for the selected period",
        #                          unique_PI_CFG.var_agg_stat[var3] + ['Min', 'Max'], key='stat3', index=0)
        #     diff_type2 = st.selectbox("Select a type of difference to compute",
        #                               [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'],
        #                               key='diff_type2')
        #     start_year3 = start_year
        #     end_year3 = end_year
        #
        #     if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':
        #
        #         gdf_grille_base = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, ze_plan_code,
        #                                                     unique_PI_CFG.available_years, stat3, var3,
        #                                                     unique_pi_module_name, start_year, end_year)
        #
        #         gdf_grille_plan = UTILS.prep_for_prep_tiles(CFG_DASHBOARD.tiles_shp, folder, PI_code, baseline_code,
        #                                                     unique_PI_CFG.available_years, stat3, var3,
        #                                                     unique_pi_module_name, start_year, end_year)
        #
        #         division_col = 'tile'
        #         gdf_both = gdf_grille_base.merge(gdf_grille_plan, on=['tile'], how='outer', suffixes=('_base', '_plan'))
        #
        #         gdf_both['geometry'] = np.where(gdf_both['geometry_base'] == None, gdf_both['geometry_plan'],
        #                                         gdf_both['geometry_base'])
        #         gdf_both = gdf_both[['tile', 'VAL_base', 'VAL_plan', 'geometry']]
        #
        #         gdf_both = gdf_both.fillna(0)
        #         gdf_both['DIFF'] = gdf_both['VAL_plan'] - gdf_both['VAL_base']
        #         gdf_both['DIFF_PROP'] = (
        #                 ((gdf_both['VAL_plan'] - gdf_both['VAL_base']) / gdf_both['VAL_base']) * 100).round(3)
        #         gdf_both = gdf_both[['tile', 'DIFF', 'DIFF_PROP', 'geometry']]
        #         gdf_both = gpd.GeoDataFrame(gdf_both, crs=4326, geometry=gdf_both['geometry'])
        #
        #         if diff_type2 == f'Values ({unit_dct[PI_code]})':
        #             data = UTILS.create_folium_map(gdf_both, 'DIFF', 1200, 700, Variable, 'diff',
        #                                            unique_pi_module_name, unit_dct[PI_code], division_col)
        #         else:
        #             data = UTILS.create_folium_map(gdf_both, 'DIFF_PROP', 1200, 700, Variable, 'diff',
        #                                            unique_pi_module_name, unit_dct[PI_code], division_col)
        #
        #         st.session_state.data = data
        #         #st.session_state.PI = PI_code
        #         st.session_state.folder = folder
        #         st.session_state.baseline_code = baseline_code
        #         st.session_state.var = var
        #         st.session_state.years = unique_PI_CFG.available_years
        #         st.session_state.ext = CFG_DASHBOARD.file_ext
        #         st.session_state.start_year = start_year3
        #         st.session_state.end_year = end_year3
        #         st.session_state.stat = stat3
        #         st.session_state.Variable = Variable
        #         st.session_state.unique_pi_module_name = unique_pi_module_name
        #         st.session_state.ze_plan_code = ze_plan_code
        #         st.session_state.unit_dct = unit_dct
        #         st.session_state.diff_type = diff_type2
        #         st.session_state.PI_code = PI_code
        #         st.session_state.ze_plan = ze_plan
        #         st.session_state.Baseline = Baseline
        #
        #         for item in st.session_state.items():
        #             print(item)
        #
        #         # if data != 'please select a tile':
        #         #     # st.link_button(
        #         #     #     url=f'./test/?data={st.session_state.data}',
        #         #     #     label=f'See tile {data} in full resolution'
        #         #     # )
        #         #     st.link_button(
        #         #         url='f./test/?pi_code={st.session_state.PI}&data={st.session_state.data}',
        #         #         label=f'See tile {data} in full resolution'
        #         #     )
        #
        #         if data != 'please select a tile':
        #             st.link_button(
        #                 url=f'./test?pi_code={PI_code}&data={data}&folder={folder}&baseline_code={baseline_code}&var={var}&years={unique_PI_CFG.available_years}&ext={CFG_DASHBOARD.file_ext}&start_year={start_year3}&end_year={end_year3}&stat={stat3}&Variable={Variable}&unique_pi_module_name={unique_pi_module_name}&ze_plan_code={ze_plan_code}&unit_dct={unit_dct}&diff_type={diff_type2}&PI_code={PI_code}&ze_plan={ze_plan}&Baseline={Baseline}',
        #                 label=f"See tile {data} in full resolution"
        #             )
        #
        #         # st.markdown(f'[Go to Test](./test?pi_code={PI_code}&data={data})')
        #
        #     else:
        #
        #         if unique_PI_CFG.divided_by_country:
        #             sct_shp = CFG_DASHBOARD.sct_poly_country
        #         else:
        #             sct_shp = CFG_DASHBOARD.sct_poly
        #
        #         gdf_grille_base = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder, PI_code,
        #                                                  baseline_code, unique_PI_CFG.available_years, stat3, var3,
        #                                                  unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
        #                                                  start_year3, end_year3, Baseline)
        #
        #         gdf_grille_plan = UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, sct_shp, folder, PI_code, ze_plan_code,
        #                                                  unique_PI_CFG.available_years, stat3, var3,
        #                                                  unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name,
        #                                                  start_year3, end_year3, Baseline)
        #
        #         division_col = 'SECTION'
        #
        #         gdf_grille_plan['DIFF'] = (gdf_grille_plan['VAL'] - gdf_grille_base['VAL']).round(3)
        #
        #         gdf_grille_plan['DIFF_PROP'] = (
        #                     ((gdf_grille_plan['VAL'] - gdf_grille_base['VAL']) / gdf_grille_base['VAL']) * 100).round(3)
        #
        #         if diff_type2 == f'Values ({unit_dct[PI_code]})':
        #             data = UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, Variable, 'diff',
        #                                            unique_pi_module_name, unit_dct[PI_code], division_col)
        #
        #         else:
        #             data = UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, Variable, 'diff',
        #                                            unique_pi_module_name, unit_dct[PI_code], division_col)
        #
        # with tab6:
        #     st.write(f'tile selected is: {data}')