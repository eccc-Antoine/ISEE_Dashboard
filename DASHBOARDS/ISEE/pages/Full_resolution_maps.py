import streamlit as st
import numpy as np # np mean, np random
import pandas as pd # read csv, df manipulation
#pd.options.mode.copy_on_write = True
pd.set_option('mode.chained_assignment', None)
import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from DASHBOARDS.UTILS import DASHBOARDS_UTILS as UTILS
import ast
import tempfile

qp = st.query_params
print(qp)

if 'pi_code' in qp and 'data' in qp:

    st.cache_data.clear()
    st.cache_resource.clear()

    for key in st.session_state.keys():
        print(st.session_state[key])

    PI_code = qp['pi_code']
    data = qp['data']
    folder = qp['folder']
    baseline_code = qp['baseline_code']
    var = qp['var']
    years = qp['years']
    ext = qp['ext']
    start_year=qp['start_year']
    end_year = qp['end_year']
    stat= qp['stat']
    Variable=qp['Variable']
    unique_pi_module_name=qp['unique_pi_module_name']
    ze_plan_code=qp['ze_plan_code']
    unit_dct=qp['unit_dct']
    diff_type=qp['diff_type']
    ze_plan = qp['ze_plan']
    Baseline = qp['Baseline']
    pi_type=qp['pi_type']

    st.write(f'Difference of :blue[{PI_code} {Variable} {stat}] between :blue[{ze_plan} and {Baseline}] from :blue[{start_year} to {end_year}]\n for tile :blue[{data}] at each ISEE 10x10m grid node')

    years=years.replace('[','')
    years = years.replace(']','')
    years = years.replace(' ', '')
    years=years.split(',')
    years=[int(x) for x in years]
    unit_dct=ast.literal_eval(unit_dct)

    df_folder_base=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  baseline_code)
    print(type)
    if pi_type=='2D_not_tiled':
        pt_id_file_base = os.path.join(df_folder_base, f'{var}_{PI_code}_YEAR_{baseline_code}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_base=UTILS.prep_data_map(pt_id_file_base, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name, pi_type, int(data))

    else:
        pt_id_file_base = os.path.join(df_folder_base, f'{var}_{PI_code}_YEAR_{baseline_code}_{int(data)}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_base=UTILS.prep_data_map(pt_id_file_base, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name,pi_type, int(data))

    df_base = df_base.sort_values(by='LAT')
    df_folder_plan=os.path.join(folder, PI_code, 'YEAR', 'PT_ID', ze_plan_code)

    if pi_type == '2D_not_tiled':
        pt_id_file_plan = os.path.join(df_folder_plan, f'{var}_{PI_code}_YEAR_{ze_plan_code}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_plan=UTILS.prep_data_map(pt_id_file_plan, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name, pi_type, int(data))


    else:
        pt_id_file_plan=os.path.join(df_folder_plan, f'{var}_{PI_code}_YEAR_{ze_plan_code}_{int(data)}_PT_ID_{np.min(years)}_{np.max(years)}{ext}')
        df_plan=UTILS.prep_data_map(pt_id_file_plan, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name, pi_type, int(data))

    df_both=df_base.merge(df_plan, on=['PT_ID'], how='outer', suffixes=('_base', '_plan'))
    df_both=df_both.fillna(0)

    if diff_type==f'Values ({unit_dct[PI_code]})':
        df_both['diff']=df_both[f'{Variable}_plan']-df_both[f'{Variable}_base']
    else:
        df_both['diff']=((df_both[f'{Variable}_plan']-df_both[f'{Variable}_base'])/df_both[f'{Variable}_base'])*100

    df_both['diff']=df_both['diff'].round(3)
    df_both.dropna(subset = ['diff'], inplace=True)

    df_both=df_both.loc[df_both['diff']!=0]

    lon_cols=[col for col in list(df_both) if 'LON' in col]
    lon_col=lon_cols[0]
    lat_cols=[col for col in list(df_both) if 'LAT' in col]
    lat_col=lat_cols[0]

    df_both['LAT']=np.where(df_both['LAT_base'] == 0, df_both['LAT_plan'], df_both['LAT_base'])
    df_both['LON']=np.where(df_both['LON_base'] == 0, df_both['LON_plan'], df_both['LON_base'])

    fig=UTILS.plot_map_plotly(Variable, df_both, 'LON', 'LAT', 'PT_ID', unique_pi_module_name, f'{ze_plan} minus {Baseline}', 'diff')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        fig.write_html(tmp_file.name)
        tmp_file.seek(0)

        st.download_button(
            label="Download map as HTML",
            data=tmp_file.read(),
            file_name="map.html",
            mime="text/html"
        )

    st.plotly_chart(fig, use_container_width=True)
