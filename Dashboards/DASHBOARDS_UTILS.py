import os
import streamlit as st
import numpy as np
import importlib
import Dashboards.CFG_DASHBOARD as CFG_DASHBOARD
from collections import namedtuple


def MAIN_FILTERS(unique_pi_module_name, Years, Region, Plans, Baselines, Stats):
    unique_PI_CFG=importlib.import_module(unique_pi_module_name, 'CFG_PIS')
      
    if Years:
        start_year, end_year=st.select_slider('Select a period', options=unique_PI_CFG.available_years, 
                                          value=(np.min(unique_PI_CFG.available_years), np.max(unique_PI_CFG.available_years)))
    else:
        start_year='N/A'
        end_year='N/A'
    
    if Region:
        available_sections={i for i in CFG_DASHBOARD.sect_dct if all(item in unique_PI_CFG.available_sections for item in  CFG_DASHBOARD.sect_dct[i])}
        Regions=st.selectbox("Select regions", available_sections)
        
    else:
        Regions='N/A'
  
    if Plans:
        available_plans={i for i in CFG_DASHBOARD.plan_dct if CFG_DASHBOARD.plan_dct[i] in unique_PI_CFG.available_plans}
        plans_selected=st.multiselect('Regulation plans to compare', available_plans, max_selections=CFG_DASHBOARD.maximum_plan_to_compare)
    else:
        plans_selected='N/A'
        
    if Baselines:
        baselines={i for i in CFG_DASHBOARD.baseline_dct if CFG_DASHBOARD.baseline_dct[i] in unique_PI_CFG.available_baselines}
        Baseline=st.selectbox("Select a reference plan", baselines)
    else:
        Baseline='N/A'

    if Stats:
        Stats=st.selectbox("Stats to compute", unique_PI_CFG.available_stats)
    else:
        Stats='N/A'
 
    return  start_year, end_year, Regions, plans_selected, Baseline, Stats 
        
    
    