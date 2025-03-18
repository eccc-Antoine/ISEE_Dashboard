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

mapbox_token='pk.eyJ1IjoidG9ueW1hcmFuZGExOTg1IiwiYSI6ImNsM3cwYm8zeDAzNHAzY3FxcWV3ZXJkbWEifQ.5rgErxAFf7_k0Kn0mz3RdA'
style_url='mapbox://styles/tonymaranda1985/clmhwft2i03rs01ph9z2kbbos'

# import datashader as ds
# import datashader.transfer_functions as tf
# import datashader.geo
# from holoviews.operation.datashader import datashade
# import holoviews as hv
# from holoviews.element.tiles import EsriImagery
# import streamlit as st
#
# # Enable HoloViews Bokeh backend
# hv.extension('bokeh')

qp = st.query_params

#qp= st.experimental_set_query_params

if 'pi_code' in qp and 'data' in qp:

    st.cache_data.clear()
    st.cache_resource.clear()

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
    ### pour s assurer quon considere correctement tous les points des tuiles qui chevauchent 2 sections
    def list_all_files(folder_path):
        liste_files=[]
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                liste_files.append(os.path.join(root, file))
        return liste_files
    liste_files=list_all_files(df_folder_base)
    tile_file=[]
    for f in liste_files:
        if f'PT_ID_{int(data)}_' in f and var in f:
            tile_file.append(f)

    if len(tile_file)==1:
        df_base=pd.read_feather(tile_file[0])
    else:
        dfs=[]
        for tf in tile_file:
            df=pd.read_feather(tf)
            dfs.append(df)
        df_base=pd.concat(dfs)
    df_base = df_base.drop_duplicates(subset='PT_ID', keep='first')

    df_base=UTILS.prep_data_map(df_base, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name)
    df_base = df_base.sort_values(by='LAT')

    df_folder_plan=os.path.join(folder, PI_code, 'YEAR', 'PT_ID', ze_plan_code)
    liste_files_plan = list_all_files(df_folder_plan)
    tile_file = []
    for f in liste_files_plan:
        if f'PT_ID_{int(data)}_' in f and var in f:
            tile_file.append(f)
    if len(tile_file) == 1:
        df_plan = pd.read_feather(tile_file[0])
    else:
        dfs = []
        for tf in tile_file:
            df = pd.read_feather(tf)
            dfs.append(df)
        df_plan = pd.concat(dfs)

    df_plan = df_plan.drop_duplicates(subset='PT_ID', keep='first')

    df_plan=UTILS.prep_data_map(df_plan, int(start_year), int(end_year), 'PT_ID', 'LAT', 'LON', stat, Variable, unique_pi_module_name)

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

    fig=UTILS.plot_map_plotly(Variable, df_both, 'LON', 'LAT', unique_pi_module_name, 'diff', mapbox_token, style_url)

    if fig =='empty':
        st.write('There is no difference between those two plans according to the widget parameters. Please, change parameters on the previous page...')

    else:
        col_map1, col_map2=st.columns(2)

        with col_map1:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                fig.write_html(tmp_file.name)
                tmp_file.seek(0)

                st.download_button(
                    label="Download map as HTML",
                    data=tmp_file.read(),
                    file_name="map.html",
                    mime="text/html"
                )

        with col_map2:

            gdf=UTILS.df_2_gdf(df_both, 'LON', 'LAT', 4326)
            shapefile_data = UTILS.save_gdf_to_zip(gdf,
                                                   f'{PI_code}_{stat}_{var}_{start_year}_{end_year}_{ze_plan_code}_minus_{baseline_code}.shp')

            st.download_button(
                label="Download map as shapefile",
                data=shapefile_data,
                file_name="difference_plan_minus_baseline.zip",
                mime="application/zip",
            )

        st.plotly_chart(fig, use_container_width=True)
