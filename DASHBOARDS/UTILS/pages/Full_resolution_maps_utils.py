import os
import numpy as np
import importlib
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import streamlit as st
import geopandas as gpd
import plotly.graph_objects as go
import numpy as np
import tempfile
import geopandas as gpd
import io
import zipfile
from shapely.geometry import Point
from DASHBOARDS.ISEE import CFG_DASHBOARD as CFG_DASHBOARD

def read_parquet_from_blob(container, blob_name):
    stream = io.BytesIO()
    data = container.download_blob(blob_name)
    data.readinto(stream)
    df = pd.read_parquet(stream,engine='pyarrow')
    if 'index' in df.columns:
        df.set_index('index',inplace=True)
    return df

def read_all_files_in_tile(container, unique_PI_CFG, plan_code, ts_code, tile_selected, var, folder):
    # Parameters
    sect_PI = unique_PI_CFG.available_sections
    PI_code = unique_PI_CFG.pi_code
    df_folder_base=os.path.join(folder, PI_code, 'YEAR', 'PT_ID',  plan_code)
    if ts_code == 'hist':
        years = st.session_state['unique_PI_CFG'].available_years_hist
    else:
        years = st.session_state['unique_PI_CFG'].available_years_future
    # Read and concatenat parquet files
    dfs = []
    for s in sect_PI:
        df_folder_section = os.path.join(df_folder_base, s)
        if int(tile_selected) in CFG_DASHBOARD.dct_tile_sect[s]:
            parquet_file = os.path.join(df_folder_section,f'{var}_{PI_code}_YEAR_{plan_code}_{s}_PT_ID_{tile_selected}_{years[0]}_{years[-1]}.parquet')
            try:
                df = read_parquet_from_blob(container, parquet_file)
                dfs.append(df)
                print('READ SUCCESSFULLY',parquet_file)
            except:
                print('OPENING FILE FAILED',parquet_file)
    # concat
    df_plan=pd.concat(dfs)
    df_plan = df_plan.drop_duplicates(subset='PT_ID', keep='first')

    return(df_plan)


def prep_data_map(df, start_year, end_year, id_col, col_x, col_y, stat, Variable, unique_pi_module_name):
    print('PREP_DATA_MAP')
    unique_PI_CFG = importlib.import_module(f"GENERAL.CFG_PIS.{unique_pi_module_name}")

    df.fillna(0, inplace=True)

    liste_year = list(range(start_year, end_year + 1))
    liste_year = [str(i) for i in liste_year]
    liste_year = [y for y in liste_year if y in list(df)]

    columns = [id_col, col_x, col_y] + liste_year
    df = df[columns]
    # Transform to numpy
    if stat == 'min':
        df['stat'] = np.nanmin(df[liste_year],axis=1)
    if stat == 'max':
        df['stat'] = np.nanmax(df[liste_year],axis=1)
    if stat == 'mean':
        df['stat'] = np.nanmean(df[liste_year],axis=1)
    if stat == 'sum':
        df['stat'] = np.nansum(df[liste_year],axis=1)

    df[Variable] = df['stat']

    multiplier = unique_PI_CFG.multiplier
    df[Variable] = (df[Variable] * multiplier).round(3)

    df = df[[id_col, col_x, col_y, Variable]]
    df.dropna(subset=[Variable], inplace=True)

    return df

def plot_map_plotly(Variable, df, col_x, col_y, unique_pi_module_name, col_value, mapbox_token, style_url):
    print('PLOT_MAP_PLOTLY')
    unique_PI_CFG = importlib.import_module(f"GENERAL.CFG_PIS.{unique_pi_module_name}")
    direction = unique_PI_CFG.var_direction[Variable]

    x_med = np.round(df[col_x].median(), 3)
    y_med = np.round(df[col_y].median(), 3)

    ### transforme les valeurs de hectares à metre carrés!
    if unique_PI_CFG.multiplier == 0.01:
        df[col_value] = df[col_value] * 10000

    df = df[['PT_ID', col_value, 'LAT', 'LON']]

    df[col_value] = df[col_value].astype(float)
    df[col_value] = df[col_value].round(3)
    df = df.dropna(subset=[col_value])

    df = df.loc[df[col_value] != 0]

    if len(df) > 10000:
        size = 7
    elif len(df) > 1000:
        size = 10
    else:
        size = 12

    value_range = [df[col_value].min(), df[col_value].max()]
    df_neg = df.loc[df[col_value] < 0]
    df_pos = df.loc[df[col_value] > 0]

    complex_green = [
        [0, "white"],
        [0.1, "#e6f5e6"],  # very light green
        [0.2, "#cceccf"],  # light green
        [0.3, "#b3e6b3"],  # light-medium green
        [0.4, "#99e699"],  # medium green
        [0.5, "#80e680"],  # medium-dark green
        [0.6, "#66e666"],  # dark green
        [0.7, "#4de64d"],  # very dark green
        [0.8, "#33e633"],  # green
        [0.9, "#1ae61a"],  # green with a hint of dark
        [1, "green"]  # green
    ]

    complex_green_inv = [
        [0, "green"],  # green
        [0.1, "#1ae61a"],  # green with a hint of dark
        [0.2, "#33e633"],  # green
        [0.3, "#4de64d"],  # very dark green
        [0.4, "#66e666"],  # dark green
        [0.5, "#80e680"],  # medium-dark green
        [0.6, "#99e699"],  # medium green
        [0.7, "#b3e6b3"],  # light-medium green
        [0.8, "#cceccf"],  # light green
        [0.9, "#e6f5e6"],  # very light green
        [1, "white"]  # white
    ]

    complex_red = [
        [0, "#800000"],  # dark red
        [0.1, "#990000"],  # slightly lighter dark red
        [0.2, "#b30000"],  # lighter dark red
        [0.3, "#cc0000"],  # medium red
        [0.4, "#e60000"],  # medium-light red
        [0.5, "#ff1a1a"],  # light red
        [0.6, "#ff3333"],  # very light red
        [0.7, "#ff6666"],  # even lighter red
        [0.8, "#ff9999"],  # very light red
        [0.9, "#ffcccc"],  # almost white with a hint of red
        [1, "white"]  # white
    ]

    complex_red_inv = [
        [0, "white"],  # white
        [0.1, "#ffcccc"],  # almost white with a hint of red
        [0.2, "#ff9999"],  # very light red
        [0.3, "#ff6666"],  # even lighter red
        [0.4, "#ff3333"],  # very light red
        [0.5, "#ff1a1a"],  # light red
        [0.6, "#e60000"],  # medium-light red
        [0.7, "#cc0000"],  # medium red
        [0.8, "#b30000"],  # lighter dark red
        [0.9, "#990000"],  # slightly lighter dark red
        [1, "#800000"]  # dark red
    ]

    if len(df_neg[col_value].unique()) == 0 and len(df_pos[col_value].unique()) == 0:
        print('simple colorscale1')
        colormap1 = 'greens'
        colormap2 = 'greens'
        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]
        empty_map = True

    elif len(df_neg[col_value].unique()) < 5 and len(df_pos[col_value].unique()) > 5:
        print('simple colorscale2')

        if direction == 'normal':
            colormap1 = complex_green
            colormap2 = 'reds_r'

        elif direction == 'inverse':
            colormap2 = 'greens_r'
            colormap1 = complex_red_inv

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]

        empty_map = False

    elif len(df_neg[col_value].unique()) > 5 and len(df_pos[col_value].unique()) < 5:
        print('simple colorscale3')

        if direction == 'normal':
            colormap1 = 'greens'
            colormap2 = complex_red_inv

        elif direction == 'inverse':
            colormap2 = 'greens_r'
            colormap1 = complex_red

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]

        empty_map = False

    elif df_pos[col_value].quantile(0.25) != df_pos[col_value].quantile(0.75) and df_neg[col_value].quantile(0.25) == \
            df_neg[col_value].quantile(0.75):
        print('simple colorscale4')

        if direction == 'normal':
            colormap1 = complex_green
            colormap2 = 'reds_r'

        elif direction == 'inverse':
            colormap2 = 'greens_r'
            colormap1 = complex_red_inv

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]

        empty_map = False

    elif df_pos[col_value].quantile(0.25) == df_pos[col_value].quantile(0.75) and df_neg[col_value].quantile(0.25) != \
            df_neg[col_value].quantile(0.75):
        print('simple colorscale5')

        if direction == 'normal':
            colormap1 = 'greens'
            colormap2 = complex_red_inv

        elif direction == 'inverse':
            colormap2 = 'greens_r'
            colormap1 = complex_red

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]

        empty_map = False

    else:
        print('complex colorscale')

        if direction == 'normal':
            colormap1 = complex_green
            colormap2 = complex_red

        elif direction == 'inverse':
            colormap2 = complex_green_inv
            colormap1 = complex_red_inv

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = (df_pos[col_value] - df_pos[col_value].quantile(0.25)) / (
                    df_pos[col_value].quantile(0.75) - df_pos[col_value].quantile(0.25))
        norm2 = (df_neg[col_value] - df_neg[col_value].quantile(0.25)) / (
                    df_neg[col_value].quantile(0.75) - df_neg[col_value].quantile(0.25))

        empty_map = False

    trace1 = go.Scattermapbox(
        lat=df_pos[col_y],
        lon=df_pos[col_x],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=size,
            color=norm1,
            colorscale=colormap1,
            cmin=0,
            cmax=1,
            opacity=1
        ),
        text=df_pos[col_value],
        hoverinfo='text',
    )

    trace2 = go.Scattermapbox(
        lat=df_neg[col_y],
        lon=df_neg[col_x],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=size,
            color=norm2,
            colorscale=colormap2,
            cmin=0,
            cmax=1,
            opacity=1
        ),
        text=df_neg[col_value],
        hoverinfo='text',
    )

    fig = go.Figure(data=[trace1, trace2])

    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            style=style_url,
            center=dict(lat=y_med, lon=x_med),
            zoom=13
        ))

    fig.update_traces(
        marker=dict(sizemode='area', sizeref=size, sizemin=size)
        # Adjust sizeref and sizemin for smaller markers
    )

    fig.update_traces(zmin=norm1.min(), zmax=norm1.max(), selector=dict(name="trace1"))
    fig.update_traces(zmin=norm2.min(), zmax=norm2.max(), selector=dict(name="trace2"))

    coords_lat = df[col_y]
    coords_lon = df[col_x]

    coordinates = [[coords_lon.min(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.max()],
                   [coords_lon.min(), coords_lat.max()]]

    fig.update_layout(mapbox_layers=[{"coordinates": coordinates}], autosize=True,
                      margin=dict(l=0, r=0, t=0, b=0),
                      height=1000)

    if empty_map:
        fig = 'empty'

    return fig

def df_2_gdf(df, xcol, ycol, crs):
    geometry = [Point(xy) for xy in zip(df[xcol], df[ycol])]
    return gpd.GeoDataFrame(df, geometry=geometry, crs=crs)

def save_gdf_to_zip(gdf, shapefile_name):
    # Create a temporary directory to store shapefile components
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Define the shapefile path (without extension)
        shapefile_path = os.path.join(tmpdirname, shapefile_name)

        # Save the GeoDataFrame to the shapefile components (.shp, .shx, .dbf, etc.)
        gdf.to_file(shapefile_path)

        # Create a zip file in memory
        zip_buffer = io.BytesIO()

        # Write all files from the temporary folder into the zip
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_name in os.listdir(tmpdirname):
                file_path = os.path.join(tmpdirname, file_name)
                zip_file.write(file_path, arcname=file_name)

        # Move the pointer to the beginning of the buffer
        zip_buffer.seek(0)

        return zip_buffer.getvalue()

def MAIN_FILTERS_streamlit_with_cache(ts_code, unique_PI_CFG, Years, Variable):
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

    return start_year, end_year, Variable

def update_session_state(key):
    st.session_state[key] = st.session_state['_'+key]

def initialize_session_state():
    # Initialize all session state used by widget
    print('INITIALIZING SESSION STATE')
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
