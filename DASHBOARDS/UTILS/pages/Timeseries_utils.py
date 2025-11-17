import os
import streamlit as st
import numpy as np
import pandas as pd
import importlib
import io
pd.set_option('mode.chained_assignment', None)
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime as dt

def read_parquet_from_blob(container, blob_name):
    print('IMPORT DATA', blob_name)
    stream = io.BytesIO()
    data = container.download_blob(blob_name)
    data.readinto(stream)
    df = pd.read_parquet(stream,engine='pyarrow')
    if 'index' in df.columns:
        df.set_index('index',inplace=True)
    return df

def header(selected_pi, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values, baseline_value,
           unit, var_direction, LakeSL_prob_1D):
    print('HEADER')
    if var_direction == 'inverse':
        delta_color = 'inverse'
    else:
        delta_color = 'normal'

    plan_values = list(map(float, plan_values))
    baseline_value = float(baseline_value)

    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(
            f':blue[{Stats}] of :blue[{selected_pi}] from :blue[{start_year} to {end_year}], in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')
    placeholder2 = st.empty()
    with placeholder2.container():
        kpis = st.columns(len(plans_selected) + 1)
        count_kpi = 1
        while count_kpi <= len(plans_selected) + 1:
            d = count_kpi - 1
            if count_kpi != len(plans_selected) + 1:
                if LakeSL_prob_1D:
                    kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit})',
                                   value=round(plan_values[d], 2), delta=0)
                else:
                    kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit})',
                                   value=round(plan_values[d], 2),
                                   delta=round(round(plan_values[d], 2) - round(baseline_value, 2), 2),
                                   delta_color=delta_color)
            else:
                kpis[d].metric(label=fr':green[Reference plan {Stats} ({unit})]',
                               value=round(baseline_value, 2), delta=0)
            count_kpi += 1

def plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, unit):
    print('PLOT_TS')

    # Import the user theme to choose the plot coloring
    theme = st.context.theme.type
    if theme=='light':
        ref_color = '#000000'
    elif theme=='dark':
        ref_color = '#ffffff'
    else:
        ref_color = "#6E6E6E"
    df_PI_plans = df_PI.loc[df_PI['PLAN'].isin(list_plans)]

    df_value_to_move = df_PI_plans[df_PI_plans['PLAN'] == Baseline]
    others = df_PI_plans[df_PI_plans['PLAN'] != Baseline]
    df_PI_plans = pd.concat([others, df_value_to_move])
    df_PI_plans = df_PI_plans.reset_index(drop=True)

    fig = go.Figure(go.Scatter(x=df_value_to_move["YEAR"],y=df_value_to_move[Variable], mode='lines', line=dict(width=3, color=ref_color, dash='dot'),
                               name=Baseline,legendgroup='Reference',legendgrouptitle_text='Reference'))

    for p in plans_selected:
        data_plan = df_PI_plans.loc[df_PI_plans['PLAN']==p]
        fig.add_trace(go.Scatter(x=data_plan["YEAR"], y=data_plan[Variable], mode='lines',
                                    name=p,legendgroup='Others',legendgrouptitle_text='Plans'))

    fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
                      xaxis_title='Years',
                      yaxis_title=f'{unit}',
                      legend=dict(groupclick='toggleitem'),
                      hovermode="x unified")
    #fig.update_yaxes(range=[full_min, full_max])

    return fig, df_PI_plans

@st.cache_data(ttl=3600)
def plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, unique_PI_CFG, LakeSL_prob_1D):
    print('PLAN AGRREGATED')

    if LakeSL_prob_1D:
        baseline_value = 0

        if Stats == 'mean':
            plan_values = []
            for c in range(len(plans_selected)):
                plan_value = np.nanmean(df_PI[Variable].loc[df_PI['PLAN'] == unique_PI_CFG.plan_dct[plans_selected[c]]])
                plan_values.append(plan_value)

        if Stats == 'sum':
            plan_values = []
            for c in range(len(plans_selected)):
                plan_value = np.sum(df_PI[Variable].loc[df_PI['PLAN'] == unique_PI_CFG.plan_dct[plans_selected[c]]])
                plan_values.append(plan_value)

    else:
        if Stats == 'mean':
            plan_values = []
            baseline_value = np.round(np.mean(df_PI[Variable].loc[df_PI['PLAN'] == unique_PI_CFG.baseline_dct[Baseline]]), 3)
            for c in range(len(plans_selected)):
                plan_value = np.nanmean(df_PI[Variable].loc[df_PI['PLAN'] == unique_PI_CFG.plan_dct[plans_selected[c]]])
                plan_values.append(plan_value)


        if Stats == 'sum':
            plan_values = []
            baseline_value = np.round(np.sum(df_PI[Variable].loc[df_PI['PLAN'] == unique_PI_CFG.baseline_dct[Baseline]]), 3)
            for c in range(len(plans_selected)):
                plan_value = np.sum(df_PI[Variable].loc[df_PI['PLAN'] == unique_PI_CFG.plan_dct[plans_selected[c]]])
                plan_values.append(plan_value)

    return baseline_value, np.round(plan_values,3)

def create_timeseries_database(folder_raw, PI_code, container):
    '''
    Create dataframe with all plan and section
    unique_pi_module_name : config of PI
    folder_raw : string to PI database (test)
    '''
    print('CREATE DATABASE')
    # Path to data
    df_folder = os.path.join(folder_raw, PI_code, 'YEAR', 'SECTION')
    df_PI = read_parquet_from_blob(container, os.path.join(df_folder,f'{PI_code}_ALL_SECTIONS.parquet'))
    return df_PI

def select_timeseries_data(df_PI, unique_PI_CFG, start_year, end_year, Region, Variable, plans_selected, Baseline):

    print('SELECT DATA')

    # PI config
    var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
    stats = unique_PI_CFG.var_agg_stat[var]

    df_PI = df_PI.loc[(df_PI['PLAN'].isin(plans_selected)) | (df_PI['PLAN'] == Baseline)]
    df_PI = df_PI.loc[df_PI['SECTION'].isin(unique_PI_CFG.sect_dct[Region])]
    df_PI = df_PI.loc[(df_PI['YEAR'] >= start_year) & (df_PI['YEAR'] <= end_year)]

    df_PI['SECTION'] = Region

    if len(unique_PI_CFG.sect_dct[Region]) > 1: # Append when region is Downstream or Upstream
        if len(stats) > 1:
            df_PI = df_PI[['YEAR', 'PLAN', 'SECTION', f'{var}_sum']]
            df_PI = df_PI.groupby(by=['YEAR', 'PLAN', 'SECTION'], as_index=False).sum()
        elif stats[0] == 'sum':
            df_PI = df_PI[['YEAR', 'PLAN', 'SECTION', f'{var}_{stats[0]}']]
            df_PI = df_PI.groupby(by=['YEAR', 'PLAN', 'SECTION'], as_index=False).sum()
        elif stats[0] == 'mean':
            df_PI = df_PI[['YEAR', 'PLAN', 'SECTION', f'{var}_{stats[0]}']]
            df_PI = df_PI.groupby(by=['YEAR', 'PLAN', 'SECTION'], as_index=False).mean()
        else:
            print('problem w. agg stat!!')

    if unique_PI_CFG.pi_code != 'CWRM_2D':
        df_PI[Variable] = df_PI[f'{var}_{stats[0]}'].fillna(0)
    else:
        df_PI[Variable] = df_PI[f'{var}_{stats[0]}']
        if 'GERBL2_2014_ComboA_STO_330' in plans_selected :
            df_PI[Variable].loc[df_PI['PLAN']=='GERBL2_2014_ComboA_STO_330'] = df_PI[Variable].loc[df_PI['PLAN']=='GERBL2_2014_ComboA_STO_330'].shift(1)
        elif 'GERBL2_2014_ComboA_RCP45' in plans_selected :
            df_PI[Variable].loc[df_PI['PLAN']=='GERBL2_2014_ComboA_RCP45'] = df_PI[Variable].loc[df_PI['PLAN']=='GERBL2_2014_ComboA_RCP45'].shift(1)

    multiplier = unique_PI_CFG.multiplier

    df_PI[Variable] = df_PI[Variable] * multiplier

    df_PI = df_PI[['YEAR', 'PLAN', 'SECTION', Variable]]

    return df_PI

def MAIN_FILTERS_streamlit(ts_code, unique_PI_CFG, Years, Region, Plans, Baselines, Stats, Variable):
    print('FILTERS')

    if Variable:
        available_variables = list(unique_PI_CFG.dct_var.values())
        Variable = st.selectbox("Select variable to display", available_variables,
                                index=available_variables.index(st.session_state['selected_variable']),
                                key='_selected_variable',on_change=update_session_state,args=('selected_variable', ))
    else:
        Variable = 'N/A'

    if Years:
        if ts_code == 'hist':
            start_year, end_year = st.slider('Select a period',
                                             min_value=unique_PI_CFG.available_years_hist[0],
                                             max_value=unique_PI_CFG.available_years_hist[-1],
                                             value=st.session_state['selected_years'],
                                             key='_selected_years',
                                             on_change=update_session_state,
                                             args=('selected_years',))
        else:
            start_year, end_year = st.slider('Select a period',
                                             min_value=unique_PI_CFG.available_years_future[0],
                                             max_value=unique_PI_CFG.available_years_future[-1],
                                             value=st.session_state['selected_years'],
                                             key='_selected_years',
                                             on_change=update_session_state,
                                             args=('selected_years',))
    else:
        start_year = 'N/A'
        end_year = 'N/A'

    if Region:
        available_sections = list(unique_PI_CFG.sect_dct.keys())
        Regions = st.selectbox("Select regions", available_sections,
                               index=available_sections.index(st.session_state['selected_section']),
                               key='_selected_section',on_change=update_session_state, args=('selected_section', ))

    else:
        Regions = 'N/A'

    if Plans:
        # available_plans=list(unique_PI_CFG.plan_dct.keys())
        available_plans = unique_PI_CFG.plans_ts_dct[ts_code]
        no_plans_for_ts = False
        if len(available_plans) == 0:
            no_plans_for_ts = True
        plans_selected = st.multiselect('Regulation plans to compare', available_plans,
                                        max_selections=10, key='_ze_plans_multiple',
                                        default=st.session_state['ze_plans_multiple'],
                                        on_change=update_session_state, args=('ze_plans_multiple', ))
    else:
        plans_selected = 'N/A'

    if Baselines:
        baselines = unique_PI_CFG.baseline_ts_dct[ts_code]

        Baseline = st.selectbox("Select a reference plan", baselines,
                                index=baselines.index(st.session_state['Baseline']),
                                key='_Baseline',on_change=update_session_state, args=('Baseline',))
    else:
        Baseline = 'N/A'

    if Stats:
        var = [key for key, value in unique_PI_CFG.dct_var.items() if value == Variable][0]
        Stats = st.selectbox("Stats to compute", unique_PI_CFG.var_agg_stat[var],
                             key='_selected_stat', on_change=update_session_state, args=('selected_stat', ))
    else:
        Stats = 'N/A'

    return start_year, end_year, Regions, plans_selected, Baseline, Stats, Variable, no_plans_for_ts

def update_session_state(key):
    st.session_state[key] = st.session_state['_'+key]

def initialize_session_state():
    # Initialize all session state used by widget
    st.session_state['unique_PI_CFG'] = importlib.import_module(f"GENERAL.CFG_PIS.CFG_{st.session_state['PI_code']}")

    # selected_variable
    available_variables = list(st.session_state['unique_PI_CFG'].dct_var.values())
    st.session_state['selected_variable'] = available_variables[0]

    # selected_years
    if st.session_state['ts_code'] == 'hist':
        years = st.session_state['unique_PI_CFG'].available_years_hist
    else:
        years = st.session_state['unique_PI_CFG'].available_years_future
    st.session_state['selected_years'] = [years[0],years[-1]]

    # selected_section
    available_sections = list(st.session_state['unique_PI_CFG'].sect_dct.keys())
    st.session_state['selected_section'] = available_sections[0]

    # selected_stat
    var = [k for k, v in st.session_state['unique_PI_CFG'].dct_var.items() if v == st.session_state['selected_variable']][0]
    st.session_state['selected_stat'] = st.session_state['unique_PI_CFG'].var_agg_stat[var][0]

    # ze_plans_multipe (plans selected to compare)
    available_plans = st.session_state['unique_PI_CFG'].plans_ts_dct[st.session_state['ts_code']]
    st.session_state['ze_plans_multiple'] = available_plans[0]

    # Baseline
    baselines=st.session_state['unique_PI_CFG'].baseline_ts_dct[st.session_state['ts_code']]
    st.session_state['Baseline']=baselines[0]

    # ze_plan
    available_plans = st.session_state['unique_PI_CFG'].plans_ts_dct[st.session_state['ts_code']]
    st.session_state['ze_plan']=available_plans[0]

    # tile_selected
    st.session_state['selected_tile'] = None

    # diff_type
    st.session_state['diff_type'] = f"Values ({st.session_state['unique_PI_CFG'].units})"


