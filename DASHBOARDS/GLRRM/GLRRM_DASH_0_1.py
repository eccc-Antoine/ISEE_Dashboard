import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import plotly.express as px # interactive charts 
import os
import importlib
import DASHBOARDS.GLRRM.CFG_GLRRM_DASH as CFG_DASHBOARD
import DASHBOARDS.UTILS.DASHBOARDS_UTILS as UTILS
from pyproj import transform, Proj
import pyproj
from pyproj import Transformer

st.set_page_config(
    page_title = 'PLAN FORMULATION Dashboard',
    page_icon = ':droplet:',
    layout = 'wide'
)

db=CFG_DASHBOARD.raw_data_base
folder=CFG_DASHBOARD.post_process_folder
loc_code=CFG_DASHBOARD.loc_list
exp_list=CFG_DASHBOARD.exp_list
st.title(CFG_DASHBOARD.title)

tab1, tab2, tab3, tab4 = st.tabs(["Reference plan comparative table", "Plan comparison table", "Difference chart", "Timeseries plot"])

with tab1: 
    st.write('Compare various candidate plans to a reference plan based on your choice of indicators')
    Col1, Col2 = st.columns([0.3, 0.7])
    with Col1:
        st.write('Filters')
    with Col2:
        st.write('Table')
    
with tab2:
    st.write('Compare various candidate plans based on on your choice of indicators')
    Col1, Col2 = st.columns([0.3, 0.7])

with tab3:
    st.write('Difference chart to compare various candidate plans to a reference plan based on a selected indicator and a selected location')
    
with tab4:
    st.write('Timeseries of selected indicators and a selected locations, to compare various candidate plans')


    
    
    #PIs= st.selectbox("Select an experiment to display", exp_list)      
    #===========================================================================
    # pi_code_set={i for i in pi_dct if pi_dct[i]==PIs}
    # for pi_code in pi_code_set:
    #     PI_code=pi_code
    # unique_pi_module_name=f'.CFG_{PI_code}'
    # unique_PI_CFG=importlib.import_module(unique_pi_module_name, 'CFG_PIS')
    #===========================================================================