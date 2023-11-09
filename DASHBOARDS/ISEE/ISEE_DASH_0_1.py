import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import plotly.express as px # interactive charts 
import os
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import CFG_ISEE_DASH as CFG_DASHBOARD
from DASHBOARDS.UTILS import DASHBOARDS_UTILS as UTILS
from pyproj import transform, Proj
import pyproj
from pyproj import Transformer
import sys



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

baseline_dct=CFG_DASHBOARD.baseline_dct
plan_dct=CFG_DASHBOARD.plan_dct

st.title(CFG_DASHBOARD.title)

Col1, Col2 = st.columns([0.2, 0.8])

with Col1: 
    PIs= st.selectbox("Select Performance indicator to display", pis)      
    pi_code_set={i for i in pi_dct if pi_dct[i]==PIs}
    for pi_code in pi_code_set:
        PI_code=pi_code
    unique_pi_module_name=f'CFG_{PI_code}'
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    
    
    start_year, end_year, Region, plans_selected, Baseline, Stats, Variable  = UTILS.MAIN_FILTERS_streamlit(unique_pi_module_name, CFG_DASHBOARD,
                                                                       Years=True, Region=True, Plans=True, Baselines=True, Stats=True, Variable=True)
    
    df_PI=UTILS.yearly_timeseries_data_prep(unique_pi_module_name, folder, PI_code, plans_selected, Baseline,  Region, start_year, end_year, Variable, CFG_DASHBOARD)

    baseline_value, plan_values=UTILS.plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, CFG_DASHBOARD)

with Col2: 
    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(f'Now showing :blue[{Stats}] of :blue[{PIs}], during :blue[{start_year} to {end_year}] period, in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')

    placeholder2 = st.empty()

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
            fig2=UTILS.plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct, CFG_DASHBOARD)
            st.plotly_chart(fig2, use_container_width=True)
             
 
        with tab3:
            st.write('put some maps here not coded yet :(')
             
         #======================================================================
         #    #### HRADCODED ### need to transfer all the data in order to work!!
         #    #precise_folder=fr'F:\LCRR_Antoine\PI_ENV\ISEE_2\LCRR\results_clean\ESLU_2D'
         #     
         #    #st.write('Please wait this is a lot of data to process :sweat_smile:')
         #     
         #    ze_plan=st.selectbox("Select a plan to display on map", plans_selected)
         #     
         #    ze_plan=plan_dct[ze_plan]
         #    
         #    
         #    #df_folder=os.path.join(raw_folder, PI_code, ze_plan,  'YEAR', 'PT_ID')
         #    df_folder=os.path.join(raw_folder, PI_code, ze_plan)
         #    
         #    #===================================================================
         #    # if not os.path.exists(df_folder):
         #    #     st.write('This level of detail is not available for this PI yet')
         #    # 
         #    # else:
         #    #===================================================================
         #    #alt=fr'{df_folder}\{ze_plan}'
         #    
         #    
         #    if unique_PI_CFG.type=='2D_tiled':
         #        liste_files=[]
         #        for root, dirs, files in os.walk(df_folder):
         #            for name in files:
         #                liste_files.append(os.path.join(root, name))
         #                        
         #        years=list(range(start_year, end_year+1))
         #        
         #        var=[k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
         #        
         #        dfs_y=[]
         #        for f in liste_files:
         #            y=int(f.split('_')[-1].replace('.csv', '')) 
         #            #print(y)
         #            sect=f.split('\\')[-3]
         #            #print(f)
         #            #print(sect)
         #            if sect in CFG_DASHBOARD.sect_dct[Region]:
         #                if y in years:
         #                    tile=f.split('_')[-2]
         #                    df_y=pd.read_csv(f, sep=';')
         #                    df_y['TILE']=int(tile)
         #                    df_y['SECTION']=sect
         #                    print(list(df_y))
         #                    
         #                    df_y=df_y[['PT_ID', f'{var}', 'SECTION', 'TILE' ]]
         #                    
         #                    
         #                    dfs_y.append(df_y)
         #                    
         #        df_p=pd.concat(dfs_y, ignore_index=True)
         #        
         #        print(list(df_p))
         #        
         #        if Stats == 'sum':
         #            df_p=df_p.groupby(by=['PT_ID', 'SECTION', 'TILE' ], as_index=False).sum()
         #        if Stats == 'average':
         #            df_p=df_p.groupby(by=['PT_ID', 'SECTION', 'TILE' ], as_index=False).mean()
         #        
         #                        ##TODO adapt so it finds the crs of each tile 
         #        transformer = Transformer.from_crs(CFG_DASHBOARD.crs, 4326)
         #         
         #        x_pts=df_p['XVAL']
         #        y_pts=df_p['YVAL']
         # 
         #        ## it works but strange!! ##  ## retested in 2020-08-16 inn still seems to be what is working... 
         #        x_proj, y_proj=transformer.transform(y_pts, x_pts)
         #        df_p['X']= x_proj
         #        df_p['Y']= y_proj
         #        
         #        df_p=df_p[['X', 'Y', f'{Variable}_sum']]
         #        
         #        st.map(df_p, latitude='Y', longitude='X', color=f'{Variable}_sum')
         #        
         #        
         #    
         #    else:
         #        print(unique_PI_CFG.type)
         #        st.write('maps not available for this type of PI yet')
         #======================================================================
   
             
        with tab4:
            df_PI['YEAR']=df_PI['YEAR'].astype(str)
            st.dataframe(df_PI.style)
            #st.dataframe(df_PI.style, hide_index=True)
     

