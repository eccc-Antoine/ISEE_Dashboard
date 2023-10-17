import os
import streamlit as st
import numpy as np
import importlib
import pandas as pd
import plotly.express as px
import Dashboards.CFG_DASHBOARD as CFG_DASHBOARD


def plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct):
    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    df_PI_plans['BASELINE_VALUE']=1
    
    for y in list(range(start_year, end_year+1)):
        for p in list_plans:
            df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==CFG_DASHBOARD.baseline_dct[Baseline])].iloc[0]
    df_PI_plans['DIFF_PROP']=((df_PI_plans[Variable]-df_PI_plans['BASELINE_VALUE'])/df_PI_plans['BASELINE_VALUE'])*100
    df_PI_plans['DIFF']=df_PI_plans[Variable]-df_PI_plans['BASELINE_VALUE']
    diff_dct={f'Values ({unit_dct[PI_code]})': 'DIFF', 'Proportion of reference value (%)': 'DIFF_PROP'}
    diff_type= st.selectbox("Select a type of difference to compute", [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'])
    fig2=px.bar(df_PI_plans, x='YEAR', y=df_PI_plans[diff_dct[diff_type]], color='ALT', barmode='group', hover_data={'ALT': True, 'YEAR': False, diff_dct[diff_type]:True})
    fig2.update_layout(title=f'Difference between each selected plans and the reference for each year of the selected time period',
           xaxis_title='Years',
           yaxis_title=f'Difference in {diff_type}')
    
    return fig2

def plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, PI_code, unit_dct):
    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    fig = px.line(df_PI_plans, x="YEAR", y=Variable, color='ALT', labels={'ALT':'Plans'})
    fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
           xaxis_title='Years',
           yaxis_title=f'{unit_dct[PI_code]}')
    return fig

def plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI):
    if Stats == 'mean':
        plan_values=[]
        baseline_value=df_PI[Variable].loc[df_PI['ALT']==CFG_DASHBOARD.baseline_dct[Baseline]].mean().round(3)
        for c in range(len(plans_selected)):
            plan_value=df_PI[Variable].loc[df_PI['ALT']==CFG_DASHBOARD.plan_dct[plans_selected[c]]].mean().round(3)
            plan_values.append(plan_value)

    if Stats == 'sum':
        plan_values=[]
        baseline_value=df_PI[Variable].loc[df_PI['ALT']==CFG_DASHBOARD.baseline_dct[Baseline]].sum().round(3)
        for c in range(len(plans_selected)):
            plan_value=df_PI[Variable].loc[df_PI['ALT']==CFG_DASHBOARD.plan_dct[plans_selected[c]]].sum().round(3)
            plan_values.append(plan_value)
            
        return baseline_value, plan_values

def yearly_timeseries_data_prep(unique_pi_module_name, folder_raw, PI_code, plans_selected, Baseline, Region, start_year, end_year, Variable):
    
    unique_PI_CFG=importlib.import_module(unique_pi_module_name, 'CFG_PIS')
    df_folder=os.path.join(folder_raw, PI_code, 'YEAR', 'SECTION')
    dfs=[]
    csv_done=[]
    plans_all=plans_selected+[Baseline]
    for p in plans_all:
        if p == Baseline:
            alt=CFG_DASHBOARD.baseline_dct[p]
        else:
            alt=CFG_DASHBOARD.plan_dct[p]
        sect=CFG_DASHBOARD.sect_dct[Region]
        for s in sect:
            csv_name=f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}.csv'
            if csv_name not in csv_done:
                df=pd.read_csv(os.path.join(df_folder, alt, s, csv_name), sep=';')
                df['ALT']=alt
                df['SECT']=s
                dfs.append(df)
                #to make sure that a same csv is not compiled more than once in the results
                csv_done.append(csv_name)
                          
    df_PI=pd.concat(dfs, ignore_index=True)
    df_PI=df_PI.loc[(df_PI['YEAR']>=start_year) & (df_PI['YEAR']<=end_year)]
    df_PI=df_PI.loc[df_PI['SECT'].isin(CFG_DASHBOARD.sect_dct[Region])]
    
    # for regions that include more than one section (ex. Canada inludes LKO_CAN and USL_CAN but we want only one value per year)
    df_PI=df_PI.groupby(by=['YEAR', 'ALT'], as_index=False).sum()
    df_PI['SECT']=Region
    unique_PI_CFG.dct_var.items()
    var=[k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
    
    df_PI[Variable]=df_PI[f'{var}_sum']
    df_PI=df_PI[['YEAR', 'ALT', 'SECT', Variable]]
    
    return df_PI

def MAIN_FILTERS_streamlit(unique_pi_module_name, Years, Region, Plans, Baselines, Stats, Variable):
    unique_PI_CFG=importlib.import_module(unique_pi_module_name, 'CFG_PIS')
    
    if Variable:
        available_variables=list(unique_PI_CFG.dct_var.values())
        Variable=st.selectbox("Select variable to display", available_variables)
    else:
        Variable='N/A'
      
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
        plans_selected=st.multiselect('Regulation plans to compare', available_plans, max_selections=CFG_DASHBOARD.maximum_plan_to_compare, default=next(iter(available_plans)))
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
    
  
 
    return  start_year, end_year, Regions, plans_selected, Baseline, Stats, Variable 
        
    
    