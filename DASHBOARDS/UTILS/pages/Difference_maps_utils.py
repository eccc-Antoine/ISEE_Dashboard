import os
import streamlit as st
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import geopandas as gpd
import branca.colormap as cm
import folium
from folium import plugins
import json
import streamlit.components.v1 as components
from DASHBOARDS.ISEE import CFG_DASHBOARD as CFG_DASHBOARD
import importlib
import tempfile
import io
import zipfile
from datetime import datetime as dt
import warnings
warnings.filterwarnings('ignore')

def read_parquet_from_blob(container, blob_name):
    stream = io.BytesIO()
    data = container.download_blob(blob_name)
    data.readinto(stream)
    df = pd.read_parquet(stream,engine='pyarrow')
    if 'index' in df.columns:
        df.set_index('index',inplace=True)
    return df

def prep_for_prep_tiles_parquet(tile_geojson, df_PI, scen_code, stat, var, unique_PI_CFG,
                                    start_year, end_year, container):

    # Load module
    multiplier = unique_PI_CFG.multiplier

    # Load tile geometries
    geojson_data = container.download_blob(f'{tile_geojson}').readall()
    gdf_tiles = gpd.read_file(geojson_data)
    gdf_tiles['TILE'] = gdf_tiles['tile'].astype(int)

    # Filter for the right section and plan
    df_PI = df_PI.loc[(df_PI['PLAN'] == scen_code)]
    df_PI = df_PI.loc[(df_PI['YEAR']>= start_year) & (df_PI['YEAR'] <= end_year)]
    df_PI = df_PI.loc[df_PI['SECTION'].isin(unique_PI_CFG.available_sections)]
    colname = df_PI.columns[df_PI.columns.str.startswith(var)][0]

    if stat == 'mean':
        df_stats = df_PI.groupby('TILE')[colname].mean().reset_index()
    elif stat == 'sum':
        df_stats = df_PI.groupby('TILE')[colname].sum().reset_index()
    elif stat == 'min':
        df_stats = df_PI.groupby('TILE')[colname].min().reset_index()
    elif stat == 'max':
        df_stats = df_PI.groupby('TILE')[colname].max().reset_index()
    else:
        raise ValueError("Unsupported stat")
    df_stats['TILE'] = df_stats['TILE'].astype(int)
    df_stats['VAL'] = (df_stats[colname] * multiplier).round(3)
    # Merge with tile geometries
    gdf_tiles = gdf_tiles.merge(df_stats[['TILE',"VAL"]], on='TILE', how="left")
    gdf_tiles = gdf_tiles.dropna(subset=["VAL"])
    gdf_tiles = gdf_tiles.loc[gdf_tiles['VAL'] != 0]

    return(gdf_tiles)

def create_folium_map(gdf_grille, col, dim_x, dim_y, var, unique_PI_CFG, division_col):
    print('FOLIUM_MAPS')
    values = gdf_grille.loc[gdf_grille[col] != 0, col]
    empty_map = False

    if len(values) == 0:
        empty_map = True
        folium_map = 0

    else:
        geometry_types = gdf_grille.geom_type.unique()[0]
        if geometry_types == 'MultiPolygon' or geometry_types == 'Polygon':
            x_med = np.round(gdf_grille.geometry.centroid.x.median(), 3)
            y_med = np.round(gdf_grille.geometry.centroid.y.median(), 3)
        else:
            x_med = np.round(gdf_grille.geometry.x.median(), 3)
            y_med = np.round(gdf_grille.geometry.y.median(), 3)

        folium_map = folium.Map(location=[y_med, x_med], zoom_start=8, tiles='cartodbpositron', height=dim_y,
                                width=dim_x)

        direction = unique_PI_CFG.var_direction[var]

        gdf_grille[col] = gdf_grille[col].astype(float)

        val_dict = gdf_grille.set_index(division_col)[col]

        centro = gdf_grille.copy(deep=True)

        gdf_grille = gdf_grille.to_crs(epsg='4326')

        gdf_grille = gdf_grille.dropna()

        centro['centroid'] = centro.centroid
        centro['centroid'] = centro["centroid"].to_crs(epsg=4326)

        gjson = gdf_grille.to_json()
        js_data = json.loads(gjson)
        val_dict = gdf_grille.set_index(division_col)[col]

        if unique_PI_CFG.type == '1D':
            if direction == 'inverse':
                linear = cm.LinearColormap(colors=['green', 'white', 'red'],
                                           index=[gdf_grille[col].quantile(0.25), 0, gdf_grille[col].quantile(0.75)],
                                           vmin=gdf_grille[col].quantile(0.25),
                                           vmax=gdf_grille[col].quantile(0.75))
            else:
                linear = cm.LinearColormap(colors=['red', 'white', 'green'],
                                           index=[gdf_grille[col].quantile(0.25), 0, gdf_grille[col].quantile(0.75)],
                                           vmin=gdf_grille[col].quantile(0.25),
                                           vmax=gdf_grille[col].quantile(0.75))

            folium.GeoJson(
                gjson,
                style_function=lambda feature: {
                    "fillColor": linear(val_dict[feature["properties"][division_col]]),
                    "color": "black",
                    "weight": 2,
                    "dashArray": "5, 5",
                },
            ).add_to(folium_map)

            for _, r in centro.iterrows():
                lat = r["centroid"].y
                lon = r["centroid"].x
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f"""<div style="font-family: courier new; color: black; font-size:20px; font-weight:bold">{r[col]}</div>""")
                    # popup="length: {} <br> area: {}".format(r["Shape_Leng"], r["Shape_Area"]),
                ).add_to(folium_map)

            linear.add_to(folium_map)

        else:
            pos_values = gdf_grille.loc[gdf_grille[col] > 0]
            pos_values = pos_values.sort_values(by=col)
            pos_values = pos_values[col]
            neg_values = gdf_grille.loc[gdf_grille[col] < 0]
            neg_values = neg_values.sort_values(by=col)
            neg_values = neg_values[col]

            if direction == 'inverse':
                neg_colormap = cm.LinearColormap(colors=['darkgreen', 'white'], vmin=neg_values.quantile(0.15), vmax=0)
                pos_colormap = cm.LinearColormap(colors=['white', 'darkred'], vmin=0, vmax=pos_values.quantile(0.85))

            else:
                neg_colormap = cm.LinearColormap(colors=['darkred', 'white'], vmin=neg_values.quantile(0.15), vmax=0)
                pos_colormap = cm.LinearColormap(colors=['white', 'darkgreen'], vmin=0, vmax=pos_values.quantile(0.85))

            if neg_values.empty:
                neg_colormap = cm.LinearColormap(colors=['white', 'white'], vmin=0, vmax=0)

            if pos_values.empty:
                pos_colormap = cm.LinearColormap(colors=['white', 'white'], vmin=0, vmax=0)

            def get_color(value):
                return neg_colormap(int(value)) if int(value) < 0 else pos_colormap(int(value))

            tooltip = folium.GeoJsonTooltip(
                fields=['TILE', col],
                aliases=['TILE', f'{var} difference'],
                localize=True,
                sticky=True,
                labels=True,
                style="""
                    background-color: #F0EFEF;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """,
                max_width=800,
            )

            popup = folium.GeoJsonPopup(
                fields=['TILE', col],
                aliases=['TILE', f'{var} difference'],
                localize=True,
                labels=True,
                style="background-color: yellow;",
            )

            g = folium.GeoJson(
                gjson,
                style_function=lambda x: {
                    "fillColor": get_color(val_dict[x["properties"][division_col]]),
                    "color": "black",
                    "fillOpacity": 0.4,
                },
                tooltip=tooltip,
                popup=popup,
            ).add_to(folium_map)

            neg_colormap.caption = "Negative Values"
            neg_colormap.add_to(folium_map)

            pos_colormap.caption = "Positive Values"
            pos_colormap.add_to(folium_map)
    return folium_map, empty_map

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

def folium_static(_fig, width, height):
    print('FOLIUM_STATIC')

    if isinstance(_fig, folium.Map):
        _fig = folium.Figure().add_child(_fig)
        return components.html(_fig.render(), height=(_fig.height or height) + 10, width=width)

    elif isinstance(_fig, plugins.DualMap):
        return components.html(_fig._repr_html_(), height=height + 10, width=width)

def prep_for_prep_1d(sct_poly, df_PI, scen_code, stat, var,
                      unique_PI_CFG, start_year, end_year, Baseline, container):
    start = dt.now()

    #df_grille_origin=read_from_sftp_gdf(filepath, sftp)
    geojson_data = container.download_blob(f'{sct_poly}').readall()
    gdf_grille_origin = gpd.read_file(geojson_data)
    gdf_grille_origin['VAL'] = np.nan

    # Load module
    multiplier = unique_PI_CFG.multiplier
    Variable = unique_PI_CFG.dct_var[var]
    sect_dct = unique_PI_CFG.sect_dct
    sect_dct = {Region : section for Region, section in sect_dct.items() if Region not in ['Upstream','Downstream']}
    reg_dct = {section[0] : Region for Region, section in sect_dct.items()}
    plans_selected = [key for key, value in unique_PI_CFG.plan_dct.items() if value == scen_code]

    df_PI = select_timeseries_data(df_PI, unique_PI_CFG, start_year, end_year,
                                   Variable, plans_selected)
    df_PI['SECTION'] = [reg_dct[section] for section in df_PI['SECTION']]
    gdf_grille_all = prep_data_map_1d(stat, gdf_grille_origin, df_PI, Variable, multiplier)
    if unique_PI_CFG.type == '1D' and 'PreProject' in plans_selected[0]:
        # Remove Lake St.Lawrence
        gdf_grille_all['VAL'].loc[gdf_grille_all['SECTION']=='Lake St.Lawrence'] = np.nan

    gdf_grille_all = gdf_grille_all.dropna(subset='VAL') # Retirer le Lac St-Laurent
    gdf_grille_all = gdf_grille_all.dissolve(by='SECTION', as_index=False)
    print('prep_for_prep_1d :', dt.now()-start)
    return gdf_grille_all

def prep_data_map_1d(stat, gdf_grille_origine, df_PI, Variable, multiplier):
    print('PREP_DATA_MAP')
    start = dt.now()
    df = df_PI
    if stat == 'min':
        val = df.groupby('SECTION')[Variable].min()
    elif stat == 'max':
        val = df.groupby('SECTION')[Variable].max()
    elif stat == 'mean':
        val = df.groupby('SECTION')[Variable].mean()
    elif stat == 'sum':
        val = df.groupby('SECTION')[Variable].sum()
    else:
        print('unavailable aggregation stat provided')
    val = val * multiplier
    val = np.round(val, 3)
    gdf_grille = gdf_grille_origine
    gdf_grille['VAL'] = gdf_grille.join(val, on='SECTION')[Variable]
    print('prep_data_map_1d :', dt.now()-start)
    return gdf_grille

def create_timeseries_database(folder_raw, PI_code, container, division):

    print('CREATE DATABASE')
    start = dt.now()
    # Path to data
    df_folder = os.path.join(folder_raw, PI_code, 'YEAR', division)
    df_PI = read_parquet_from_blob(container, os.path.join(df_folder,f'{PI_code}_ALL_{division}S{CFG_DASHBOARD.file_ext}'))
    print('create_timeseries_database :', dt.now()-start)
    return(df_PI)

# Check for some stuff regarding Saint-Laurent lake (see old function, yearly_timeseries_data_prep_map)
def select_timeseries_data(df_PI, unique_PI_CFG, start_year, end_year, Variable, plans_selected):

    print('SELECT DATA')
    start = dt.now()

    var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
    stats = unique_PI_CFG.var_agg_stat[var]

    df_PI = df_PI.loc[(df_PI['PLAN'].isin(plans_selected))]
    df_PI = df_PI.loc[(df_PI['YEAR'] >= start_year) & (df_PI['YEAR'] <= end_year)]
    df_PI[Variable] = df_PI[f'{var}_{stats[0]}']

    multiplier = unique_PI_CFG.multiplier

    df_PI[Variable] = df_PI[Variable] * multiplier

    df_PI = df_PI[['YEAR', 'PLAN', 'SECTION', Variable]]
    print('select_timeseries_data :', dt.now()-start)
    return df_PI

def MAIN_FILTERS_streamlit_simple(ts_code, unique_PI_CFG, Years, Variable):
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
    st.session_state['ze_plans_multiple_name'] = st.session_state['unique_PI_CFG'].plan_dct[available_plans[0]]

    # Baseline
    baselines=st.session_state['unique_PI_CFG'].baseline_ts_dct[st.session_state['ts_code']]
    st.session_state['Baseline']=baselines[0]
    st.session_state['Baseline_name']=st.session_state['unique_PI_CFG'].baseline_dct[baselines[0]]

    # ze_plan
    available_plans = st.session_state['unique_PI_CFG'].plans_ts_dct[st.session_state['ts_code']]
    st.session_state['ze_plan']=available_plans[0]
    st.session_state['ze_plan_name']=st.session_state['unique_PI_CFG'].plan_dct[available_plans[0]]

    # tile_selected
    st.session_state['selected_tile'] = None

    # diff_type
    st.session_state['diff_type'] = f"Values ({st.session_state['unique_PI_CFG'].units})"
