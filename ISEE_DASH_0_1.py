import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import plotly.express as px # interactive charts 
import os
import plotly.figure_factory as ff
import importlib
import Dashboards.CFG_DASHBOARD as CFG_DASHBOARD
import Dashboards.DASHBOARDS_UTILS as UTILS
import altair

st.set_page_config(
    page_title = 'ISEE Dashboard',
    page_icon = ':floppy_disk:',
    layout = 'wide'
)

folder=CFG_DASHBOARD.post_process_folder 

pis_code=os.listdir(folder)
pi_dct={}
unit_dct={}
for pi in pis_code:
    pi_module_name=f'.CFG_{pi}'
    PI_CFG=importlib.import_module(pi_module_name, 'CFG_PIS')
    pi_name=PI_CFG.name
    pi_unit=PI_CFG.units
    pi_dct[pi]=pi_name
    unit_dct[pi]=pi_unit

pis=[]
for pi in pis_code:
    pi_name=pi_dct[pi]
    pis.append(pi_name)

baseline_dct=CFG_DASHBOARD.baseline_dct
plan_dct=CFG_DASHBOARD.plan_dct

st.title(CFG_DASHBOARD.title)

Col1, Col2 = st.columns([0.2, 0.8])

with Col1: 
    PIs= st.selectbox("Select Performance indicator to display", pis)      
    pi_code_set={i for i in pi_dct if pi_dct[i]==PIs}
    for pi_code in pi_code_set:
        PI_code=pi_code
    unique_pi_module_name=f'.CFG_{PI_code}'
    unique_PI_CFG=importlib.import_module(unique_pi_module_name, 'CFG_PIS')
    start_year, end_year, Region, plans_selected, Baseline, Stats, Variable  = UTILS.MAIN_FILTERS_streamlit(unique_pi_module_name,
                                                                       Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)


with Col2: 
    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(f'Now showing :blue[{Stats}] of :blue[{PIs}], during :blue[{start_year} to {end_year}] period, in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')

    placeholder2 = st.empty()
    
    df_PI=UTILS.yearly_timeseries_data_prep(unique_pi_module_name, folder, PI_code, plans_selected, Baseline,  Region, start_year, end_year, Variable)

    baseline_value, plan_values=UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI)

    with placeholder2.container():  
        kpis = st.columns(CFG_DASHBOARD.maximum_plan_to_compare)
        count_kpi=1
        while count_kpi <= len(plans_selected):
            d=count_kpi-1
            kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit_dct[PI_code]})', value=round(plan_values[d]), delta= round(plan_values[d]) -round(baseline_value))
            count_kpi+=1
            
    placeholder3 = st.empty()
    with placeholder3.container():
        tab1, tab2, tab3, tab4 = st.tabs(["Timeseries", "Difference", "Maps", "Data"])
        list_plans=[]
        for p in plans_selected:
            pp=plan_dct[p]
            list_plans.append(pp)
        list_plans.append(baseline_dct[Baseline])

        with tab1:
            fig=UTILS.plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, PI_code,  unit_dct)
            st.plotly_chart(fig, use_container_width=True)
         
        with tab2:  
            fig2=UTILS.plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct)
            st.plotly_chart(fig2, use_container_width=True)
             
 
        with tab3:
            st.write('put some maps here not coded yet :(')
             
            #===================================================================
            # #### HRADCODED ### need to tranfer all the data in order to work!!
            # precise_folder=fr'F:\LCRR_Antoine\PI_ENV\ISEE_2\LCRR\results_clean\ESLU_2D'
            # 
            # #st.write('Please wait this is a lot of data to process :sweat_smile:')
            # 
            # ze_plan=st.selectbox("Select a plan to display on map", plans_selected)
            # 
            # ze_plan=plan_dct[ze_plan]
            # 
            # #for p in list_plans:
            # alt=fr'{precise_folder}\{ze_plan}'
            # dfs_s=[]
            # for s in sect_dct[Region]:
            #     reg=fr'{alt}\Section_{s}'
            #     tiles=os.listdir(reg)
            #     dfs_t=[]
            #     for t in tiles:
            #         print(tiles)
            #         dfs_y=[]
            #         tile=fr'{reg}\{t}'
            #         for y in list(range(start_year, end_year+1)):
            #             ### HARDCODED ###
            #             df_y=pd.read_csv(fr'{tile}\ESLU_2D_CAN_{y}_Section_{s}_{t}.csv', sep=';')
            #             df_y=df_y[['PT_ID', 'XVAL', 'YVAL', 'HSI']]
            #             dfs_y.append(df_y)
            #         df_t=pd.concat(dfs_y, ignore_index=True)
            #         dfs_t.append(df_t)
            #     df_s=pd.concat(dfs_t, ignore_index=True)
            #     dfs_s.append(df_s)
            # df_p=pd.concat(dfs_s, ignore_index=True)
            # if Stats == 'sum':
            #     df_p=df_p.groupby(by=['PT_ID', 'XVAL', 'YVAL'], as_index=False).sum()
            # if Stats == 'average':
            #     df_p=df_p.groupby(by=['PT_ID', 'XVAL', 'YVAL'], as_index=False).mean()
            # print(df_p.head())
            # #st.write('done!')
            # print(len(df_p))
            # print(len(df_p['PT_ID'].unique()))         
            #===================================================================

             
        with tab4:
            df_PI['YEAR']=df_PI['YEAR'].astype(str)
            st.dataframe(df_PI.style, hide_index=True)
     

