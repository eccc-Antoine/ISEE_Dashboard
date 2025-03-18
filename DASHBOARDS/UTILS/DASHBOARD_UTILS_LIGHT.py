import os
import streamlit as st
import numpy as np
import importlib
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import plotly.express as px
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components
from DASHBOARDS.ISEE import CFG_ISEE_DASH_LIGHT as CFG_DASHBOARD
import numpy as np
import tempfile
import streamlit as st
import io
import zipfile
import paramiko

hostname = 'sanijcfilesharingprod.blob.core.windows.net'
port = 22
username = 'sanijcfilesharingprod.amaranda'
password = 'fk8alyBfLpgSz+8zh/3Qq1UqKcqYoyiG'

def connect_sftp():
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return sftp, transport


def sftp_close(sftp, transport):
    sftp.close()
    transport.close()

def read_from_sftp(filepath, sftp):
    filepath = filepath.replace('\\', '/')
    print(filepath)
    try:
        with sftp.open(filepath, 'r') as remote_file:
            if CFG_DASHBOARD.file_ext == '.feather':
                df = pd.read_feather(remote_file)
            else:
                df = pd.read_csv(remote_file, sep=';')

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return df

@st.cache_data(ttl=3600)
def header(selected_pi, Stats, start_year, end_year, Region, plans_selected, Baseline, plan_values,
           baseline_value, PI_code, unit_dct, var_direction, LakeSL_prob_1D):
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
                    kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit_dct[PI_code]})',
                                   value=round(plan_values[d], 2), delta=0)
                else:
                    kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit_dct[PI_code]})',
                                   value=round(plan_values[d], 2),
                                   delta=round(round(plan_values[d], 2) - round(baseline_value, 2), 2),
                                   delta_color=delta_color)
            else:
                kpis[d].metric(label=fr':green[Reference plan {Stats} ({unit_dct[PI_code]})]',
                               value=round(baseline_value, 2), delta=0)
            count_kpi += 1

@st.cache_data(ttl=3600)
def plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct,
                               unique_pi_module_name, diff_type):
    print('PLOT_DTS')
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_PI_plans = df_PI.loc[df_PI['ALT'].isin(list_plans)]
    df_PI_plans['BASELINE_VALUE'] = 1.0

    for y in list(range(start_year, end_year + 1)):
        for p in list_plans:
            ### WORKAROUND so if value is missing it still continues....
            if len(df_PI_plans[Variable].loc[
                       (df_PI_plans['YEAR'] == y) & (df_PI_plans['ALT'] == unique_PI_CFG.baseline_dct[Baseline])]) > 0:
                df_PI_plans.loc[(df_PI_plans['YEAR'] == y) & (df_PI_plans['ALT'] == p), 'BASELINE_VALUE'] = \
                df_PI_plans.loc[(df_PI_plans['YEAR'] == y) & (
                            df_PI_plans['ALT'] == unique_PI_CFG.baseline_dct[Baseline]), Variable].iloc[0].round(3)
            else:
                df_PI_plans.loc[(df_PI_plans['YEAR'] == y) & (df_PI_plans['ALT'] == p), 'BASELINE_VALUE'] = 0.000001

    df_PI_plans['DIFF_PROP'] = ((df_PI_plans[Variable] - df_PI_plans['BASELINE_VALUE']) / df_PI_plans[
        'BASELINE_VALUE']) * 100
    df_PI_plans['DIFF_PROP'] = df_PI_plans['DIFF_PROP'].round(3)
    df_PI_plans['DIFF'] = df_PI_plans[Variable] - df_PI_plans['BASELINE_VALUE']
    df_PI_plans['DIFF'] = df_PI_plans['DIFF'].round(3)
    diff_dct = {f'Values ({unit_dct[PI_code]})': 'DIFF', 'Proportion of reference value (%)': 'DIFF_PROP'}
    fig2 = px.bar(df_PI_plans, x='YEAR', y=df_PI_plans[diff_dct[diff_type]], color='ALT', barmode='group',
                  hover_data={'ALT': True, 'YEAR': True, diff_dct[diff_type]: True})
    fig2.update_layout(
        title=f'Difference between each selected plans and the reference for each year of the selected time period',
        xaxis_title='Years',
        yaxis_title=f'Difference in {diff_type}')

    return fig2, df_PI_plans

@st.cache_data(ttl=3600)
def plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, PI_code, unit_dct):
    print('PLOT_TS')
    df_PI_plans = df_PI.loc[df_PI['ALT'].isin(list_plans)]

    df_value_to_move = df_PI_plans[df_PI_plans['ALT'] == Baseline]
    others = df_PI_plans[df_PI_plans['ALT'] != Baseline]
    df_PI_plans = pd.concat([others, df_value_to_move])
    df_PI_plans = df_PI_plans.reset_index(drop=True)

    fig = px.line(df_PI_plans, x="YEAR", y=Variable, color='ALT', labels={'ALT': 'Plans'})
    fig['data'][-1]['line']['color'] = "#00ff00"
    fig['data'][-1]['line']['width'] = 3
    fig['data'][-1]['line']['dash'] = 'dash'

    fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
                      xaxis_title='Years',
                      yaxis_title=f'{unit_dct[PI_code]}')
    return fig, df_PI_plans

@st.cache_data(ttl=3600)
def plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, unique_PI_CFG, LakeSL_prob_1D):
    print('PLAN AGRREGATED')
    multiplier = unique_PI_CFG.multiplier
    if LakeSL_prob_1D:
        baseline_value = 0

        if Stats == 'mean':
            plan_values = []
            for c in range(len(plans_selected)):
                plan_value = df_PI[Variable].loc[
                    df_PI['ALT'] == unique_PI_CFG.plan_dct[plans_selected[c]]].mean().round(3)
                plan_values.append(plan_value)

        if Stats == 'sum':
            plan_values = []
            for c in range(len(plans_selected)):
                plan_value = df_PI[Variable].loc[df_PI['ALT'] == unique_PI_CFG.plan_dct[plans_selected[c]]].sum().round(
                    3)
                plan_values.append(plan_value)

    else:
        if Stats == 'mean':
            plan_values = []
            baseline_value = df_PI[Variable].loc[df_PI['ALT'] == unique_PI_CFG.baseline_dct[Baseline]].mean().round(3)
            for c in range(len(plans_selected)):
                plan_value = df_PI[Variable].loc[
                    df_PI['ALT'] == unique_PI_CFG.plan_dct[plans_selected[c]]].mean().round(3)
                plan_values.append(plan_value)

        if Stats == 'sum':
            plan_values = []
            baseline_value = df_PI[Variable].loc[df_PI['ALT'] == unique_PI_CFG.baseline_dct[Baseline]].sum().round(3)
            for c in range(len(plans_selected)):
                plan_value = df_PI[Variable].loc[df_PI['ALT'] == unique_PI_CFG.plan_dct[plans_selected[c]]].sum().round(
                    3)
                plan_values.append(plan_value)

    return baseline_value, plan_values

#@st.cache_data(ttl=3600)
def yearly_timeseries_data_prep(ts_code, unique_pi_module_name, folder_raw, PI_code, plans_selected, Baseline, Region,
                                start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D, sftp):
    print('TIMESERIES_PREP')

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_folder = os.path.join(folder_raw, PI_code, 'YEAR', 'SECTION')
    dfs = []
    feather_done = []

    var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
    stats = unique_PI_CFG.var_agg_stat[var]
    if len(stats) > 1:
        var_s = f'{var}_sum'
    elif stats[0] == 'sum':
        var_s = f'{var}_sum'
    elif stats[0] == 'mean':
        var_s = f'{var}_mean'
    else:
        print('problem w. agg stat!!')

    if LakeSL_prob_1D:
        plans_all = plans_selected
    else:
        plans_all = plans_selected + [Baseline]

    for p in plans_all:

        if p == Baseline:
            alt = unique_PI_CFG.baseline_dct[p]
        else:
            alt = unique_PI_CFG.plan_dct[p]

        sect = unique_PI_CFG.sect_dct[Region]

        for s in sect:
            if ts_code == 'hist':
                feather_name = f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years_hist)}_{np.max(unique_PI_CFG.available_years_hist)}{CFG_DASHBOARD.file_ext}'
            else:
                feather_name = f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years_future)}_{np.max(unique_PI_CFG.available_years_future)}{CFG_DASHBOARD.file_ext}'

            if feather_name not in feather_done:
                filepath = os.path.join(df_folder, alt, s, feather_name)
                df = read_from_sftp(filepath, sftp)
                df['ALT'] = alt
                df['SECT'] = s

                dfs.append(df)
                # to make sure that a same feather is not compiled more than once in the results
                feather_done.append(feather_name)

    df_PI = pd.concat(dfs, ignore_index=True)
    df_PI = df_PI.loc[(df_PI['YEAR'] >= start_year) & (df_PI['YEAR'] <= end_year)]
    df_PI = df_PI.loc[df_PI['SECT'].isin(unique_PI_CFG.sect_dct[Region])]

    df_PI['SECT'] = Region
    # when a variable can be aggregated by mean or sum, sum is done in priority
    if len(stats) > 1:
        df_PI = df_PI[['YEAR', 'ALT', 'SECT', var_s]]
        df_PI = df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).sum()
    elif stats[0] == 'sum':
        df_PI = df_PI[['YEAR', 'ALT', 'SECT', var_s]]
        df_PI = df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).sum()
    elif stats[0] == 'mean':
        df_PI = df_PI[['YEAR', 'ALT', 'SECT', var_s]]
        df_PI = df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).mean()
    else:
        print('problem w. agg stat!!')

    df_PI[Variable] = df_PI[f'{var}_{stats[0]}']

    multiplier = unique_PI_CFG.multiplier

    df_PI[Variable] = df_PI[Variable] * multiplier

    df_PI = df_PI[['YEAR', 'ALT', 'SECT', Variable]]

    return df_PI

def MAIN_FILTERS_streamlit(ts_code, unique_pi_module_name, CFG_DASHBOARD, Years, Region, Plans, Baselines, Stats,
                           Variable):
    print('FILTERS')

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

    if Variable:
        available_variables = list(unique_PI_CFG.dct_var.values())
        Variable = st.selectbox("Select variable to display", available_variables, index=0)
    else:
        Variable = 'N/A'

    if Years:
        if ts_code == 'hist':
            start_year, end_year = st.select_slider('Select a period', options=unique_PI_CFG.available_years_hist,
                                                    value=(np.min(unique_PI_CFG.available_years_hist),
                                                           np.max(unique_PI_CFG.available_years_hist)))
        else:
            start_year, end_year = st.select_slider('Select a period', options=unique_PI_CFG.available_years_future,
                                                    value=(np.min(unique_PI_CFG.available_years_future),
                                                           np.max(unique_PI_CFG.available_years_future)))
    else:
        start_year = 'N/A'
        end_year = 'N/A'

    if Region:
        available_sections = list(unique_PI_CFG.sect_dct.keys())
        Regions = st.selectbox("Select regions", available_sections)

    else:
        Regions = 'N/A'

    if Plans:
        available_plans = unique_PI_CFG.plans_ts_dct[ts_code]
        no_plans_for_ts = False
        if len(available_plans) == 0:
            no_plans_for_ts = True
        plans_selected = st.multiselect('Regulation plans to compare', available_plans,
                                        max_selections=CFG_DASHBOARD.maximum_plan_to_compare,
                                        default=next(iter(available_plans)))
    else:
        plans_selected = 'N/A'

    if Baselines:
        # baselines= list(unique_PI_CFG.baseline_dct.keys())
        baselines = unique_PI_CFG.baseline_ts_dct[ts_code]

        # baselines = [item for item in baselines if item not in plans_selected]
        Baseline = st.selectbox("Select a reference plan", baselines)
    else:
        Baseline = 'N/A'

    if Stats:
        var = [key for key, value in unique_PI_CFG.dct_var.items() if value == Variable][0]
        Stats = st.selectbox("Stats to compute", unique_PI_CFG.var_agg_stat[var])
    else:
        Stats = 'N/A'

    return start_year, end_year, Regions, plans_selected, Baseline, Stats, Variable, no_plans_for_ts
