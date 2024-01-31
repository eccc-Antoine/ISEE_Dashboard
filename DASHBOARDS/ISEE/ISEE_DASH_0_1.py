import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
#pd.options.mode.copy_on_write = True
pd.set_option('mode.chained_assignment', None)
import plotly.express as px # interactive charts 
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


st.set_page_config(
    page_title = 'ISEE Dashboard',
    page_icon = ':floppy_disk:',
    layout = 'wide'
)


raw_folder=CFG_DASHBOARD.raw_data_folder
folder=CFG_DASHBOARD.post_process_folder
pis_code=CFG_DASHBOARD.pi_list

pi_dct={}
unit_dct={}
for pi in pis_code:
    pi_module_name=f'CFG_{pi}'
    PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    pi_type=PI_CFG.type
    pi_name=PI_CFG.name
    pi_unit=PI_CFG.units
    pi_dct[pi]=pi_name
    unit_dct[pi]=pi_unit

pis=[]
for pi in pis_code:
    pi_name=pi_dct[pi]
    pis.append(pi_name)

#baseline_dct=CFG_DASHBOARD.baseline_dct
#plan_dct=CFG_DASHBOARD.plan_dct

st.title(CFG_DASHBOARD.title)

Col1, Col2 = st.columns([0.2, 0.8])

with Col1: 
    PIs= st.selectbox("Select Performance indicator to display", pis)      
    pi_code_set={i for i in pi_dct if pi_dct[i]==PIs}
    for pi_code in pi_code_set:
        PI_code=pi_code
    unique_pi_module_name=f'CFG_{PI_code}'
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    start_year, end_year, Region, plans_selected, Baseline, Stats, Variable  = UTILS.MAIN_FILTERS_streamlit(unique_pi_module_name, CFG_DASHBOARD,
                                                                       Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)
    var_direction=unique_PI_CFG.var_direction[Variable]
    
    df_PI=UTILS.yearly_timeseries_data_prep(unique_pi_module_name, folder, PI_code, plans_selected, Baseline,  Region, start_year, end_year, Variable, CFG_DASHBOARD)

    baseline_value, plan_values=UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, unique_PI_CFG)

with Col2:         
    placeholder3 = st.empty()
    with placeholder3.container():
        tab2, tab3, tab4, tab5, tab6 = st.tabs(["Timeseries", "Difference", "Maps", "Difference Maps", "Data"])
        list_plans=[]
        for p in plans_selected:
            pp=unique_PI_CFG.plan_dct[p]
            list_plans.append(pp)
        list_plans.append(unique_PI_CFG.baseline_dct[Baseline])
        
        with tab2:
            max_plans=CFG_DASHBOARD.maximum_plan_to_compare
            UTILS.header(Stats, PIs, start_year, end_year, Region, plans_selected, Baseline, max_plans, plan_values, baseline_value, PI_code, unit_dct,  var_direction)
            fig=UTILS.plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, PI_code,  unit_dct)
            st.plotly_chart(fig, use_container_width=True)
         
        with tab3:
            diff_type= st.selectbox("Select a type of difference to compute", [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'])
            UTILS.header(Stats, PIs, start_year, end_year, Region, plans_selected, Baseline, max_plans, plan_values, baseline_value, PI_code, unit_dct, var_direction)
            fig2=UTILS.plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct, unique_pi_module_name, diff_type)
            st.plotly_chart(fig2, use_container_width=True)

        with tab4:            
            Col1, Col2 = st.columns([0.5, 0.5], gap='small')
            with Col1:
                
                #baselines={i for i in CFG_DASHBOARD.baseline_dct if CFG_DASHBOARD.baseline_dct[i] in unique_PI_CFG.available_baselines}
                baselines=list(unique_PI_CFG.baseline_dct.keys())
                Baseline=st.selectbox("Select a reference plan to display", baselines)                    
                           
                baseline_code=unique_PI_CFG.baseline_dct[Baseline]
                var=[k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
                stat1=st.selectbox("Select a way to aggregate values for the selected period", unique_PI_CFG.var_agg_stat[var]+['Min', 'Max'], key='stat1', index=0)         
                if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':

                    df_folder=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  baseline_code, unique_PI_CFG.sect_dct[Region][0])
                     
                    pt_id_file=os.path.join(df_folder, f'{var}_{PI_code}_YEAR_{baseline_code}_{unique_PI_CFG.sect_dct[Region][0]}_PT_ID_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}{CFG_DASHBOARD.file_ext}')
                     
                    df=UTILS.prep_data_map(pt_id_file, start_year, end_year, 'PT_ID', 'X_COORD', 'Y_COORD', stat1, Variable)

                    fig=UTILS.plot_map_plotly(PIs, Variable, df, 'X_COORD', 'Y_COORD', 'PT_ID', unique_pi_module_name, Baseline, Variable)    
                        
                    st.plotly_chart(fig, use_container_width=True) 
    
                else: 
                    gdf_grille=UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, CFG_DASHBOARD.sct_poly, folder, PI_code, baseline_code, unique_PI_CFG.available_years, stat1, var, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name)
                    folium_map=UTILS.create_folium_map(gdf_grille, 'VAL', 700, 700, Baseline, stat1, Variable, 'compare') 
                    UTILS.folium_static(folium_map, 700, 700)
                                         
            with Col2:
                available_plans={i for i in unique_PI_CFG.plan_dct if unique_PI_CFG.plan_dct[i] in unique_PI_CFG.available_plans}
                ze_plan=st.selectbox("Select a candidate plan to display", available_plans)
                ze_plan_code=unique_PI_CFG.plan_dct[ze_plan]
                var2=[k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
                st.selectbox("", ['', ''], key='stat2', index=0)
                if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':
                
                    df_folder=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  ze_plan_code, unique_PI_CFG.sect_dct[Region][0])
                    pt_id_file=os.path.join(df_folder, f'{var}_{PI_code}_YEAR_{ze_plan_code}_{unique_PI_CFG.sect_dct[Region][0]}_PT_ID_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}{CFG_DASHBOARD.file_ext}')
                    df=UTILS.prep_data_map(pt_id_file, start_year, end_year, 'PT_ID', 'X_COORD', 'Y_COORD', stat1, Variable)
                    fig=UTILS.plot_map_plotly(PIs, Variable, df, 'X_COORD', 'Y_COORD', 'PT_ID', unique_pi_module_name, ze_plan, Variable)    
                    st.plotly_chart(fig, use_container_width=True) 
                else:                    
                    gdf_grille=UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, CFG_DASHBOARD.sct_poly, folder, PI_code, ze_plan_code, unique_PI_CFG.available_years, stat1, var2, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name)
                    folium_map=UTILS.create_folium_map(gdf_grille, 'VAL', 700, 700, ze_plan, stat1, Variable, 'compare') 
                    UTILS.folium_static(folium_map, 700, 700)
                
                
        with tab5:        
            ze_plan=st.selectbox("Select a regulation plan to compare with reference plan", plans_selected)
            
            baseline_code=unique_PI_CFG.baseline_dct[Baseline]
            ze_plan_code=unique_PI_CFG.plan_dct[ze_plan]
            var3=[k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
            stat3=st.selectbox("Select a way to aggregate values for the selected period", unique_PI_CFG.var_agg_stat[var3]+['Min', 'Max'], key='stat3', index=0)   
            diff_type2= st.selectbox("Select a type of difference to compute", [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'], key='diff_type2')
            if unique_PI_CFG.type == '2D_tiled' or unique_PI_CFG.type == '2D_not_tiled':

                df_folder_base=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  baseline_code, unique_PI_CFG.sect_dct[Region][0]) 
                pt_id_file_base=os.path.join(df_folder_base, f'{var}_{PI_code}_YEAR_{baseline_code}_{unique_PI_CFG.sect_dct[Region][0]}_PT_ID_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}{CFG_DASHBOARD.file_ext}')
                df_base=UTILS.prep_data_map(pt_id_file_base, start_year, end_year, 'PT_ID', 'X_COORD', 'Y_COORD', stat3, Variable)
                   
                df_folder_plan=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  ze_plan_code, unique_PI_CFG.sect_dct[Region][0]) 
                pt_id_file_plan=os.path.join(df_folder_plan, f'{var}_{PI_code}_YEAR_{ze_plan_code}_{unique_PI_CFG.sect_dct[Region][0]}_PT_ID_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}{CFG_DASHBOARD.file_ext}')
                df_plan=UTILS.prep_data_map(pt_id_file_plan, start_year, end_year, 'PT_ID', 'X_COORD', 'Y_COORD', stat3, Variable)
                
                df_both=df_base.merge(df_plan, on=['PT_ID', 'X_COORD', 'Y_COORD'], how='outer', suffixes=('_base', '_plan'))
                if diff_type2==f'Values ({unit_dct[PI_code]})':
                    df_both['diff']=df_both[f'{Variable}_plan']-df_both[f'{Variable}_base']
                else:
                    df_both['diff']=((df_both[f'{Variable}_plan']-df_both[f'{Variable}_base'])/df_both[f'{Variable}_base'])*100
                    
                df_both['diff']=df_both['diff'].round(3)
                df_both.dropna(subset = ['diff'], inplace=True)
                
                fig=UTILS.plot_map_plotly(PIs, Variable, df_both, 'X_COORD', 'Y_COORD', 'PT_ID', unique_pi_module_name, f'{ze_plan} minus {Baseline}', 'diff')
                st.plotly_chart(fig, use_container_width=True) 
                

            else:
                gdf_grille_base=UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, CFG_DASHBOARD.sct_poly, folder, PI_code, baseline_code, unique_PI_CFG.available_years, stat3, var3, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name)
            
                gdf_grille_plan=UTILS.prep_for_prep_1d(unique_PI_CFG.sect_dct, CFG_DASHBOARD.sct_poly, folder, PI_code, ze_plan_code, unique_PI_CFG.available_years, stat3, var3, unique_PI_CFG.mock_map_sct_dct, unique_pi_module_name)
                   
                gdf_grille_plan['DIFF']=(gdf_grille_plan['VAL']-gdf_grille_base['VAL']).round(3)
                
                gdf_grille_plan['DIFF_PROP']=(((gdf_grille_plan['VAL']-gdf_grille_base['VAL'])/gdf_grille_base['VAL'])*100).round(3)
                
                if diff_type2==f'Values ({unit_dct[PI_code]})':
                    folium_map=UTILS.create_folium_map(gdf_grille_plan, 'DIFF', 1200, 700, ze_plan, stat3, Variable, 'diff') 
                else:
                    folium_map=UTILS.create_folium_map(gdf_grille_plan, 'DIFF_PROP', 1200, 700, ze_plan, stat3, Variable, 'diff')
                    
                UTILS.folium_static(folium_map, 1200, 700)

             
        with tab6:
            df_PI['YEAR']=df_PI['YEAR'].astype(str)
            st.dataframe(df_PI.style)

