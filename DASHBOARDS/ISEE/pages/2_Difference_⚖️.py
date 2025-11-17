import streamlit as st
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import importlib
from pathlib import Path
import traceback
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
import DASHBOARDS.ISEE.CFG_DASHBOARD as CFG_DASHBOARD
from DASHBOARDS.UTILS.pages import Difference_utils as UTILS
from azure.storage.blob import BlobServiceClient
from datetime import datetime as dt

st.set_page_config(
    page_title='ISEE Dashboard - GLAM Project',
    page_icon='🏞️',
    layout='wide',
    initial_sidebar_state='collapsed')

def set_base_path():
    CFG_DASHBOARD.post_process_folder = CFG_DASHBOARD.post_process_folder_name

set_base_path()

start = dt.now()

folder = CFG_DASHBOARD.post_process_folder # Pas clair
pis_code = CFG_DASHBOARD.pi_list # PI list
tss_code=CFG_DASHBOARD.ts_list # Timeserie list

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

st.title('PI Differences ⚖️')
st.subheader('Select what you want to see on the left and display the results on the right.', divider="gray")

def function_for_tab2():

    # Deux colonnes : une avec les widgets et une avec le graphiques
    Col1, Col2 = st.columns([0.2, 0.8],gap='large')
    with Col1:
        st.subheader('**Parameters**')
        # Afficher la colonne 1 (gauche)
        LakeSL_prob_1D, selected_pi, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts=render_column1()

    with Col2:
        st.subheader('**Plot**')
        diff_type = st.selectbox("Select a type of difference to compute",
                                     [f'Values ({unique_PI_CFG.units})', 'Proportion of reference value (%)'], key='select3')

        if no_plans_for_ts==True:
            st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

        else:
            unique_PI_CFG = st.session_state['unique_PI_CFG']

            UTILS.header(selected_pi, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values,
                                baseline_value, unique_PI_CFG.units, var_direction, LakeSL_prob_1D)

            if LakeSL_prob_1D:
                st.write(':red[For 1D PIs, It is not possible to have values compared to PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet!]')


            fig2, df_PI_plans = UTILS.plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year,
                                                                 unique_PI_CFG.units, unique_PI_CFG, diff_type)

            csv_data = df_PI_plans.to_csv(index=False, sep=';')

            st.download_button(
                    label="Download displayed data in CSV format",
                    data=csv_data,
                    file_name="dataframe.csv",
                    mime="text/csv",
                    key='db_2')

            st.plotly_chart(fig2, use_container_width=True)

def render_column1():

    old_PI_code = st.session_state['PI_code']
    old_ts_code = st.session_state['ts_code']
    ts_list = list(ts_dct.values())
    timeseries = st.selectbox("Select a supply", ts_list, index=ts_list.index(ts_dct[st.session_state['ts_code']]), key='timeseries')
    update_timeseries()
    pi_list = list(pi_dct.values())
    pi_list.sort()
    selected_pi = st.selectbox("Select a Performance Indicator", pi_list,
                               index=pi_list.index(pi_dct[st.session_state['PI_code']]),
                               key='_selected_pi')
    update_PI_code()

    PI_code = st.session_state['PI_code']
    ts_code = st.session_state['ts_code']
    unique_PI_CFG = st.session_state['unique_PI_CFG']

    # First time loading the dashboard
    if 'df_PI_timeseries' not in st.session_state:
        st.session_state['df_PI_timeseries'] = UTILS.create_timeseries_database(folder, PI_code, st.session_state['azure_container'])
    # If the use changed the PI, load it
    if (old_PI_code != st.session_state['PI_code']):
        st.session_state['df_PI_timeseries'] = UTILS.create_timeseries_database(folder, PI_code, st.session_state['azure_container'])
        # when the timeserie changes, the value of the widgets need to change too
        UTILS.initialize_session_state()
    if (old_ts_code != st.session_state['ts_code']):
        UTILS.initialize_session_state()

    df_PI = st.session_state['df_PI_timeseries']

    start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, no_plans_for_ts = UTILS.MAIN_FILTERS_streamlit(ts_code,unique_PI_CFG,
            Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)

    LakeSL_prob_1D =False
    if unique_PI_CFG.type=='1D'and Region=='Lake St.Lawrence' and 'PreProject' in Baseline :
        LakeSL_prob_1D=True

    var_direction = unique_PI_CFG.var_direction[Variable]

    df_PI = UTILS.select_timeseries_data(df_PI, unique_PI_CFG, start_year, end_year, Region, Variable, plans_selected, Baseline)

    baseline_value, plan_values = UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI,
                                                                   unique_PI_CFG, LakeSL_prob_1D)

    list_plans = []
    for p in plans_selected:
        pp = unique_PI_CFG.plan_dct[p]
        list_plans.append(pp)
    if unique_PI_CFG.baseline_dct[Baseline] not in list_plans:
        list_plans.append(unique_PI_CFG.baseline_dct[Baseline])

    return LakeSL_prob_1D, selected_pi, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts

try:
    function_for_tab2()
    st.session_state['has_resetted'] = False
except Exception as e:
    if not st.session_state['has_resetted']:
        st.warning('An error occurred, restarting the dashboard now...')
        st.error(traceback.format_exc())

        st.session_state['PI_code'] = pis_code[0]
        st.session_state['selected_pi'] = default_PI
        st.session_state['ts_code'] = tss_code[0]
        st.session_state['selected_timeseries'] = default_ts
        st.session_state['df_PI_timeseries'] = UTILS.create_timeseries_database(folder, st.session_state['PI_code'], st.session_state['azure_container'])

        UTILS.initialize_session_state()
        st.session_state['has_resetted'] = True
        st.rerun()
    else:
        st.error('An error occurred and persisted. Please close the dashboard and open it again. If you are still not able to use the dashboard, please contact us and we will assist you. We are sorry for the inconvenience.')
        st.error(traceback.format_exc())

st.sidebar.caption('This app was developed by the Hydrodynamic and Ecohydraulic Services of the National Hydrological Service ' \
                'at Environment and Climate Change Canada, based on results from the Integrated Social, Economic, and Environmental System (ISEE).')

print('Execution time:',dt.now()-start)
print('-------------END-------------')