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
from DASHBOARDS.UTILS.pages import Timeseries_utils as UTILS
from azure.storage.blob import BlobServiceClient
from datetime import datetime as dt


st.set_page_config(
    page_title='ISEE Dashboard - GLAM Project',
    page_icon='🏞️',
    layout='wide',
    initial_sidebar_state='collapsed')
st.sidebar.caption('This app was developed by the Hydrodynamic and Ecohydraulic Services of the National Hydrological Service ' \
                'at Environment and Climate Change Canada, based on results from the Integrated Social, Economic, and Environmental System (ISEE).')

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

wl_dct={'WL_ISEE_1D':'ISEE', 'WL_GLRRM_1D':'GLRRM' }

# Pretty name of pi
pis = list(pi_dct.values())

ts_dct={'hist':'historical', 'sto':'stochastic', 'cc':'climate change'}

default_PI=next(iter(pi_dct.values()), None)
default_ts=next(iter(ts_dct.values()), None)
default_WL=next(iter(wl_dct.values()), None)

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

if 'WL_code' not in st.session_state:
    st.session_state['WL_code'] = list(wl_dct.keys())[0]
    st.session_state['selected_wl'] = default_WL

if '_WL_code' not in st.session_state:
    st.session_state['_WL_code'] = list(wl_dct.keys())[0]
    st.session_state['_selected_wl'] = default_WL

if 'unique_PI_CFG' not in st.session_state:
    PI_code = st.session_state['PI_code']
    st.session_state['unique_PI_CFG'] = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{PI_code}')

if 'WL_PI_CFG' not in st.session_state:
    WL_code = st.session_state['WL_code']
    st.session_state['WL_PI_CFG'] = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{WL_code}')

if 'azure_container' not in st.session_state:
    # connect to Azur blob storage
    blob_service_client = BlobServiceClient(CFG_DASHBOARD.azure_url, credential = CFG_DASHBOARD.access_key)
    container = blob_service_client.get_container_client('dukc-db')
    st.session_state['azure_container'] = container
    # If azure container is not in session state, it means it's the first time loading a page, since we have this on all pages
    UTILS.initialize_session_state()

if 'water_level' not in st.session_state:
    st.session_state['water_level'] = "No"

if 'wl_plan_name' not in st.session_state:
    st.session_state['wl_plan_name'] = "N/A"

# Change PI or Timeserie
def update_PI_code():
    st.session_state['selected_pi'] = st.session_state['_selected_pi']
    selected_pi_name = st.session_state['selected_pi']
    pi_code = [key for key, value in pi_dct.items() if value == selected_pi_name]
    st.session_state['PI_code'] = pi_code[0]
    st.session_state['unique_PI_CFG'] = importlib.import_module(f"GENERAL.CFG_PIS.CFG_{pi_code[0]}")

def update_WL_code():
    st.session_state['selected_wl'] = st.session_state['_selected_wl']
    selected_wl_name = st.session_state['selected_wl']
    wl_code = [key for key, value in wl_dct.items() if value == selected_wl_name]
    st.session_state['WL_code'] = wl_code[0]
    st.session_state['WL_PI_CFG'] = importlib.import_module(f"GENERAL.CFG_PIS.CFG_{wl_code[0]}")

def update_timeseries():
    selected_timeseries = st.session_state['timeseries']
    ts_code = [key for key, value in ts_dct.items() if value == selected_timeseries]
    st.session_state['ts_code'] = ts_code[0]

st.title('PI Timeseries 📈')
st.subheader('Select what you want to see on the left and display the results on the right.', divider="gray")

def function_for_tab1():

    # # Deux colonnes : une avec les widgets et une avec le graphiques
    Col1, Col2 = st.columns([0.2, 0.8],gap='large') # Deux colonnes dans l'affichage
    with Col1:
    #with st.sidebar.expander("Dashboard Parameters", expanded=True):
        st.subheader('**Parameters**')
        LakeSL_prob_1D, selected_pi, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts, show_water_levels, wl_plan_selected, df_WL, WL_var, WL_PI_CFG=render_column1()

    #Col1, Col2 = st.columns([0.05, 0.95], gap='large')  # Deux colonnes dans l'affichage
    with Col2:
        st.subheader('**Plot**')
        if no_plans_for_ts==True:
            st.write(':red[There is no plan available yet for this PI with the supply that is selected, please select another supply]')

        else:
            unique_PI_CFG = st.session_state['unique_PI_CFG']
            WL_PI_CFG= st.session_state['WL_PI_CFG']

            UTILS.header(selected_pi, unique_PI_CFG, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values,
                                baseline_value, unique_PI_CFG.units, var_direction, LakeSL_prob_1D)

            if LakeSL_prob_1D:
                st.write(':red[For 1D PIs, It is not possible to have values for PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet! \n This is why PreProjectHistorical values do not appear on the plot below, and are not considered int he difference calculation.]')

            upstream_warning = False

            if wl_plan_selected is not None:
                if 'PreProjectHistorical' in wl_plan_selected and Region =='Upstream':
                    upstream_warning=True
                if 'PreProjectHistorical' in wl_plan_selected and Region =='Lake St.Lawrence':
                    st.write(
                        ':red[For 1D water levels, It is not possible to have values for PreProjectHistorical in Lake St. Lawrence since the Lake was not created yet! \n This is why water level values do not appear on the plot below.]')

            if 'WL' in unique_PI_CFG.pi_code and Region == 'Upstream' and ('PreProjectHistorical' in plans_selected or 'PreProjectHistorical' in Baseline) :
                upstream_warning = True
            if upstream_warning:
                st.write(':red[Note that for PreProjectHistorical, Lake St. Lawrence is not included in the Upstream section values. This explaina surprisingly high values comparing to other plans for the Upstream section (which include Lake St. Lawrence)]')

            fig, df_PI_plans = UTILS.plot_timeseries(df_PI, unique_PI_CFG, list_plans, Variable, plans_selected, Baseline,
                                                     start_year, end_year, unique_PI_CFG.units, show_water_levels, wl_plan_selected, df_WL, WL_var)

            csv_data=df_PI_plans.to_csv(index=False, sep=';')
            st.download_button(
                    label="Download displayed data in CSV",
                    data=csv_data,
                    file_name="dataframe.csv",
                    mime="text/csv",
                    key='db_1')

            st.plotly_chart(fig, use_container_width=True)

def render_column1():

    old_ts_code = st.session_state['ts_code']
    ts_list = list(ts_dct.values())
    st.selectbox("Select a supply", ts_list, index=ts_list.index(ts_dct[st.session_state['ts_code']]), key='timeseries')
    update_timeseries()

    old_PI_code = st.session_state['PI_code']
    old_WL_code = st.session_state['WL_code']
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
    # If the user changed the PI, load it
    if (old_PI_code != st.session_state['PI_code']):
        st.session_state['df_PI_timeseries'] = UTILS.create_timeseries_database(folder, PI_code, st.session_state['azure_container'])
        # when the timeserie changes, the value of the widgets need to change too
        UTILS.initialize_session_state()
    if (old_ts_code != st.session_state['ts_code']):
        UTILS.initialize_session_state()


    df_PI = st.session_state['df_PI_timeseries']


    start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, no_plans_for_ts, show_water_level, wl_plan_selected = UTILS.MAIN_FILTERS_streamlit(ts_code,unique_PI_CFG,
            Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True, water_levels=True)

    WL_PI_CFG=st.session_state['WL_PI_CFG']

    if show_water_level=='Yes':
        wl_list = list(wl_dct.values())
        wl_list.sort()
        selected_wl = st.selectbox("From ISEE or GLRRM ?", wl_list,
                                   index=wl_list.index(wl_dct[st.session_state['WL_code']]),
                                   key='_selected_wl')


        wl_var = st.selectbox("Annual mean, min or max?", ['Min', 'Mean', 'Max'],
                                   index=1,
                                   key='_wl_var')
    else:
        if '_wl_var' not in st.session_state:
            st.session_state['_wl_var'] = 'Mean'

    wl_var_dct={'Min':'VAR1', 'Mean':'VAR2', 'Max':'VAR3'}

    wl_var_code= wl_var_dct[st.session_state['_wl_var']]
    wl_variable=WL_PI_CFG.dct_var[wl_var_code]

    update_WL_code()
    WL_code = st.session_state['WL_code']

    # First time loading the dashboard
    if 'df_WL_timeseries' not in st.session_state:
        st.session_state['df_WL_timeseries'] = UTILS.create_timeseries_database(folder, WL_code, st.session_state['azure_container'])
    # If the user changed the PI, load it
    if (old_WL_code != st.session_state['WL_code']):
        st.session_state['df_WL_timeseries'] = UTILS.create_timeseries_database(folder, WL_code, st.session_state['azure_container'])
        # when the timeserie changes, the value of the widgets need to change too
        UTILS.initialize_session_state()
    if (old_ts_code != st.session_state['ts_code']):
        UTILS.initialize_session_state()

    #st.session_state['df_WL_timeseries'] = UTILS.create_timeseries_database(folder, WL_code, st.session_state['azure_container'])
    df_WL = st.session_state['df_WL_timeseries']

    LakeSL_prob_1D =False
    if unique_PI_CFG.type=='1D'and Region=='Lake St.Lawrence' and ('PreProject' in Baseline or 'PreProjectHistorical' in plans_selected):
        LakeSL_prob_1D=True

    var_direction = unique_PI_CFG.var_direction[Variable]
    df_PI, Variable = UTILS.select_timeseries_data(df_PI, unique_PI_CFG, start_year, end_year, Region, Variable, plans_selected, Baseline)

    if unique_PI_CFG.divided_by_country==True:
        Region_WL=Region.replace(' Canada', '')
        Region_WL2=Region_WL.replace(' United States', '')
    else:
        Region_WL2=Region

    if wl_plan_selected is not None:
        df_WL, WL_var = UTILS.select_timeseries_data(df_WL, WL_PI_CFG, start_year, end_year, Region_WL2,  wl_variable, wl_plan_selected,
                                             'N/A')

        #print(df_WL['YEAR'].unique())

    else:
        df_WL=None
        WL_var=None

    baseline_value, plan_values = UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI,
                                                                   unique_PI_CFG, LakeSL_prob_1D)

    list_plans = plans_selected.copy()
    if Baseline not in list_plans:
        list_plans.append(Baseline)


    return LakeSL_prob_1D, selected_pi, PI_code, unique_PI_CFG, start_year, end_year, Region, plans_selected, Baseline, Stats, Variable, var_direction, df_PI, baseline_value, plan_values, list_plans, no_plans_for_ts, show_water_level, wl_plan_selected, df_WL, WL_var, WL_PI_CFG

try:
    function_for_tab1()
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

print('Execution time:',dt.now()-start)
print('-------------END-------------')