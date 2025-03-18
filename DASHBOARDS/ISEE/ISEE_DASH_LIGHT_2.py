import streamlit as st  # web development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation

pd.set_option('mode.chained_assignment', None)
import plotly.express as px  # interactive charts
import os
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DASH_LIGHT as CFG_DASHBOARD
from DASHBOARDS.UTILS import DASHBOARD_UTILS_LIGHT as UTILS
import tempfile
import sys
import streamlit.components.v1 as components


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

sftp, transport=UTILS.connect_sftp()

st.set_page_config(
    page_title='ISEE Dashboard',
    page_icon=':floppy_disk:',
    layout='wide',
    initial_sidebar_state="collapsed"

)

folder = CFG_DASHBOARD.post_process_folder
pis_code = CFG_DASHBOARD.pi_list
tss_code=CFG_DASHBOARD.ts_list

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

        df_PI= UTILS.yearly_timeseries_data_prep(ts_code, unique_pi_module_name, folder, PI_code, plans_selected, Baseline, Region, start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D, sftp)


        baseline_value, plan_values = UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI,
                                                                   unique_PI_CFG, LakeSL_prob_1D)

        list_plans = []
        for p in plans_selected:
            pp = unique_PI_CFG.plan_dct[p]
            list_plans.append(pp)
        list_plans.append(unique_PI_CFG.baseline_dct[Baseline])

    return folder, LakeSL_prob_1D, selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts

button_col1, button_col2 = st.columns(2)

switch_tab('Timeseries')

with button_col1:
    if st.button('Timeseries'):
        switch_tab('Timeseries')

with button_col2:
    if st.button('Difference'):
        switch_tab('Difference')


if st.session_state['active_tab'] == 'Timeseries':

    function_for_tab1(exec=True)

elif st.session_state['active_tab'] == 'Difference':
    function_for_tab2(exec=True)


else:
    exec=False