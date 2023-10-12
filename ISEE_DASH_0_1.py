import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import plotly.express as px # interactive charts 
import os
import plotly.figure_factory as ff
import importlib
import Dashboards.CFG_DASHBOARD as CFG_DASHBOARD
import Dashboards.DASHBOARDS_UTILS as UTILS

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
        pi_code=pi_code
    unique_pi_module_name=f'.CFG_{pi_code}'
    
    start_year, end_year, Regions, plans_selected, Baseline, Stats  = UTILS.MAIN_FILTERS(unique_pi_module_name,
                                                                       Years=True, Region=True, Plans=True, Baselines=True, Stats=True)
    
with Col2: 
    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(f'Now showing :blue[{Stats}] of :blue[{PIs}], during :blue[{start_year} to {end_year}] period, in :blue[{Regions}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')

    placeholder2 = st.empty()
    
    key_list = list(pi_dct.keys())
    val_list = list(pi_dct.values())
    position = val_list.index(PIs)
    PI_code=key_list[position]
    
    df_PI=pd.read_csv(os.path.join(folder, f'{PI_code}_alts.csv'), sep=';')

    ##filters
    #year
    df_PI=df_PI.loc[(df_PI['YEAR']>=start_year) & (df_PI['YEAR']<=end_year)]
    #region
    df_PI=df_PI.loc[df_PI['SECT_ID'].isin(sect_dct[Region])]
    
    #merge by year if more than one region selected 
    df_PI=df_PI[['YEAR', 'VALUE', 'ALT']]
    df_PI=df_PI.groupby(by=['YEAR', 'ALT'], as_index=False).sum()
        
    if Stats == 'average':
        baseline_value=df_PI['VALUE'].loc[df_PI['ALT']==baseline_dct[Baseline]].mean().round(3)
        if len(plans_selected)>0:
            plan1_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[0]]].mean().round(3)
        if len(plans_selected)>1:
            plan2_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[1]]].mean().round(3)
        if len(plans_selected)>2:
            plan3_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[2]]].mean().round(3)
        
    if Stats == 'sum':
        baseline_value=df_PI['VALUE'].loc[df_PI['ALT']==baseline_dct[Baseline]].sum().round(3)
        if len(plans_selected)>0:
            plan1_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[0]]].sum().round(3)
        if len(plans_selected)>1:
            plan2_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[1]]].sum().round(3)
        if len(plans_selected)>2:
            plan3_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[2]]].sum().round(3)

    with placeholder2.container():
    # create three columns
        kpi1, kpi2, kpi3 = st.columns(3)
        
        if len(plans_selected)==0:
            st.write('You must at least select one regulation plan to compare')
        
        if len(plans_selected)>0:
        #kpi1.metric(label="Age", value=round(avg_age), delta= round(avg_age) - 10)
            kpi1.metric(label=fr'{plans_selected[0]} {Stats} ({unit_dct[PI_code]})', value=round(plan1_value), delta= round(plan1_value) -round(baseline_value))
        
        if len(plans_selected)>1:
        #kpi2.metric(label="Married Count ðŸ’�", value= int(count_married), delta= - 10 + count_married)
            kpi2.metric(label=fr'{plans_selected[1]} {Stats} ({unit_dct[PI_code]})', value=round(plan2_value), delta= round(plan2_value) -round(baseline_value))
        
        if len(plans_selected)>2:
        #kpi3.metric(label="A/C Balance ï¼„", value= f"$ {round(balance,2)} ", delta= - round(balance/count_married) * 100)
            kpi3.metric(label=fr'{plans_selected[2]} {Stats} ({unit_dct[PI_code]})', value=round(plan3_value), delta= round(plan3_value) -round(baseline_value))
    
    placeholder3 = st.empty()
    with placeholder3.container():
        tab1, tab2, tab3, tab4 = st.tabs(["Timeseries", "Difference", "Maps", "Data"])
        list_plans=[]
        for p in plans_selected:
            pp=plan_dct[p]
            list_plans.append(pp)
        #list_plans= plan_dct[plans_selected]
        list_plans.append(baseline_dct[Baseline])
        
        with tab1:
            df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
            fig = px.line(df_PI_plans, x="YEAR", y="VALUE", color='ALT')
            fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
                   xaxis_title='Years',
                   yaxis_title=f'{unit_dct[PI_code]}')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:  
            df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
            df_PI_plans['BASELINE_VALUE']=1

            for y in list(range(start_year, end_year+1)):
                for p in list_plans:
                    df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = df_PI_plans['VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==baseline_dct[Baseline])].iloc[0]

            df_PI_plans['DIFF_PROP']=((df_PI_plans['VALUE']-df_PI_plans['BASELINE_VALUE'])/df_PI_plans['BASELINE_VALUE'])*100
            df_PI_plans['DIFF']=df_PI_plans['VALUE']-df_PI_plans['BASELINE_VALUE']
            diff_dct={f'Values ({unit_dct[PI_code]})': 'DIFF', 'Proportion of reference value (%)': 'DIFF_PROP'}
            diff_type= st.selectbox("Select a type of difference to compute", [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'])
            fig2=px.bar(df_PI_plans, x='YEAR', y=df_PI_plans[diff_dct[diff_type]], color='ALT', barmode='group', hover_data={'ALT': True, 'YEAR': False, diff_dct[diff_type]:True})
            fig2.update_layout(title=f'Difference between each selected plans and the reference for each year of the selected time period',
                   xaxis_title='Years',
                   yaxis_title=f'Difference in {diff_type}')
            st.plotly_chart(fig2, use_container_width=True)
            

        with tab3:
            
            st.write('put some maps here')
            
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
                            
            
            
            
            
    #===========================================================================
    #         df_PI_precise=pd.read_csv(fr'{folder}\{PI_code}_precise.csv', sep=';')
    #             ##filters
    #         #year
    #         df_PI_precise=df_PI_precise.loc[(df_PI_precise['YEAR']>=start_year) & (df_PI_precise['YEAR']<=end_year)]
    #         
    #         #region
    #         df_PI_precise=df_PI_precise.loc[df_PI_precise['SECT_ID'].isin(sect_dct[Region])]
    #         
    #         #merge by year if more than one region selected >1:
    #         df_PI_precise=df_PI_precise[['YEAR', 'VALUE', 'ALT']]
    #         df_PI_precise=df_PI_precise.groupby(by=['YEAR', 'ALT'], as_index=False).sum()
    # 
    #         'put some maps here'
    #===========================================================================
            
        with tab4:
            #'put some Data here'
            df_PI['YEAR']=df_PI['YEAR'].astype(str)
            st.dataframe(df_PI.style, hide_index=True)
    

