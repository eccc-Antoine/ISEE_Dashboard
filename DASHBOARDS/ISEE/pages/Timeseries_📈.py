import streamlit as st
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import os
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DUCK as CFG_DASHBOARD
from DASHBOARDS.UTILS.pages import Timeseries_utils as UTILS
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

st.title('PI Timeseries 📈')
st.subheader('Select what you want to see on the left and display the results on the right.', divider="gray")

def function_for_tab1():

    # Deux colonnes : une avec les widgets et une avec le graphiques
    Col1, Col2 = st.columns([0.2, 0.8],gap='large') # Deux colonnes dans l'affichage
    with Col1:
        st.subheader('**Parameters**')
        # Afficher la colonne 1 (gauche)
        folder, LakeSL_prob_1D, selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts=render_column1()

    with Col2:
        st.subheader('**Plot**')
        if no_plans_for_ts==True:
            st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

        else:
            UTILS.header(selected_pi, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values,
                                baseline_value, PI_code, unit_dct, var_direction, LakeSL_prob_1D)

            if LakeSL_prob_1D:
                st.write(':red[For 1D PIs, It is not possible to have values compared to PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet! \n This is why delta values are all equal to 0 and why the Baseline values do not appear on the plot below.]')

            fig, df_PI_plans = UTILS.plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year,
                                                    PI_code, unit_dct)
            csv_data=df_PI_plans.to_csv(index=False, sep=';')

            st.download_button(
                    label="Download displayed data in CSV format",
                    data=csv_data,
                    file_name="dataframe.csv",
                    mime="text/csv",
                    key='db_1')
            st.plotly_chart(fig, use_container_width=True)

def render_column1():

    old_ts_code = st.session_state['ts_code']
    old_PI_code = st.session_state['PI_code']

    timeseries = st.selectbox("Select a supply", ts_dct.values(), key='timeseries')
    update_timeseries()

    selected_pi = st.selectbox("Select a Performance Indicator", list(pi_dct.values()), key='selected_pi')
    update_PI_code()

    PI_code = st.session_state['PI_code']
    unique_pi_module_name = f'CFG_{PI_code}'
    ts_code = st.session_state['ts_code']

    # First time loading the dashboard
    if 'df_PI' not in st.session_state:
        st.session_state['df_PI'] = UTILS.create_timeseries_database(ts_code, unique_pi_module_name, folder, PI_code)

    if (old_ts_code != st.session_state['ts_code']) or (old_PI_code != st.session_state['PI_code']):
        PI_code = st.session_state['PI_code']
        unique_pi_module_name = f'CFG_{PI_code}'
        ts_code = st.session_state['ts_code']
        st.session_state['df_PI'] = UTILS.create_timeseries_database(ts_code, unique_pi_module_name, folder, PI_code)

    df_PI = st.session_state['df_PI']

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

    start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, no_plans_for_ts = UTILS.MAIN_FILTERS_streamlit(ts_code,
            unique_pi_module_name, CFG_DASHBOARD,
            Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)
    # print(plans_selected)
    LakeSL_prob_1D =False
    if unique_PI_CFG.type=='1D'and Region=='Lake St.Lawrence' and 'PreProject' in Baseline :
        LakeSL_prob_1D=True

    var_direction = unique_PI_CFG.var_direction[Variable]

    df_PI = UTILS.select_timeseries_data(df_PI, unique_pi_module_name, start_year, end_year, Region, Variable, plans_selected, Baseline)

    baseline_value, plan_values = UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI,
                                                                   unique_PI_CFG, LakeSL_prob_1D)

    list_plans = []
    print(plans_selected)
    for p in plans_selected:
        pp = unique_PI_CFG.plan_dct[p]
        list_plans.append(pp)
    if unique_PI_CFG.baseline_dct[Baseline] not in list_plans:
        list_plans.append(unique_PI_CFG.baseline_dct[Baseline])

    return folder, LakeSL_prob_1D, selected_pi, unique_pi_module_name, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts

function_for_tab1()