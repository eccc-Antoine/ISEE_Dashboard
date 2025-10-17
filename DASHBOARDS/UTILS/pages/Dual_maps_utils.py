import os
import streamlit as st
import numpy as np
import importlib
import pandas as pd

pd.set_option('mode.chained_assignment', None)
import geopandas as gpd
import branca.colormap as cm
import folium
from folium import plugins
import json
import streamlit.components.v1 as components
from DASHBOARDS.ISEE import CFG_ISEE_DUCK as CFG_DASHBOARD
import numpy as np
import tempfile
import streamlit as st
import geopandas as gpd
import io
import zipfile
import duckdb

def prep_for_prep_tiles_duckdb_lazy(tile_geojson, folder, PI_code, scen_code, avail_years, stat, var, unique_pi_module_name,
                                    start_year, end_year, sas_token, container_url):
    print('PREP_FOR_PREP_TILES_DUCKDB_LAZY')

    # Load module
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    multiplier = unique_PI_CFG.multiplier
    sect_PI = unique_PI_CFG.available_sections

    # Load tile geometries
    geojson_url = f"{container_url}/{tile_geojson}?{sas_token}"
    gdf_tiles = gpd.read_file(geojson_url)

    # Build list of parquet URLs
    parquet_files = []
    for s in sect_PI:
        for t in CFG_DASHBOARD.dct_tile_sect[s]:
            df_folder = os.path.join(folder, PI_code, 'YEAR', 'TILE', scen_code, s, str(t))
            parquet_file = os.path.join(
                df_folder,
                f'{PI_code}_YEAR_{scen_code}_{s}_{t}_{np.min(avail_years)}_{np.max(avail_years)}.parquet'
            )
            parquet_files.append(parquet_file.replace('\\', '/'))

    parquet_urls = [f"{container_url}/{f}?{sas_token}" for f in parquet_files]

    # Connect to DuckDB (in-memory)
    con = duckdb.connect(database=':memory:')

    # Create a view directly on the Parquet files (lazy, no reading yet)
    urls_str = ', '.join([f"'{url}'" for url in parquet_urls])
    con.execute(f"CREATE VIEW tiles AS SELECT * FROM parquet_scan([{urls_str}])")

    # Determine aggregation expression
    sample_cols = con.execute("DESCRIBE tiles").fetchall()
    sample_cols = [c[0] for c in sample_cols]

    if f'{var}_mean' in sample_cols:
        col_name = f'{var}_mean'
    elif f'{var}_sum' in sample_cols:
        col_name = f'{var}_sum'
    else:
        raise ValueError(f"Variable '{var}' not found in parquet columns")

    if stat not in ['mean', 'sum', 'min', 'max']:
        raise ValueError("Unsupported stat")

    agg_expr = f"{stat}({col_name}) * {multiplier}"

    # Build SQL query
    sql = f"""
        SELECT tile,
               round({agg_expr}, 3) AS VAL
        FROM tiles
        WHERE YEAR BETWEEN {start_year} AND {end_year}
        GROUP BY tile
    """

    # Execute lazily
    df_stats = con.execute(sql).df()

    df_stats['tile'] = df_stats['tile'].astype(int)

    # Merge with tile geometries
    gdf_tiles = gdf_tiles.merge(df_stats, on="tile", how="left")
    gdf_tiles = gdf_tiles.dropna(subset=["VAL"])
    gdf_tiles = gdf_tiles.loc[gdf_tiles['VAL'] != 0]

    return gdf_tiles

def prep_for_prep_1d(ts_code, sect_dct, sct_poly, folder, PI_code, scen_code, avail_years, stat, var,
                     unique_pi_module_name, start_year, end_year, Baseline, sas_token, container_url):
    print('PREP_FOR_PREP_1D')

    filepath = sct_poly.replace('\\', '/')

    #df_grille_origin=read_from_sftp_gdf(filepath, sftp)

    shp_url = f"{container_url}/{sct_poly}?{sas_token}"

    gdf_grille_origin=gpd.read_file(shp_url)

    #gdf_grille_origin = gpd.read_file(filepath)
    #gdf_grille_origin['VAL'] = 0.0

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    gdfs = []

    list_sect = sect_dct.keys()

    for s in list_sect:
        df_folder = os.path.join(folder, PI_code, 'YEAR', 'SECTION', scen_code, s)
        plans_selected = [key for key, value in unique_PI_CFG.plan_dct.items() if value == scen_code]
        if plans_selected == []:
            plans_selected = [key for key, value in unique_PI_CFG.baseline_dct.items() if value == scen_code]
        Variable = unique_PI_CFG.dct_var[var]

        if s == 'Lake St.Lawrence':
            LakeSL_prob_1D = False
            if unique_PI_CFG.type == '1D' and s == 'Lake St.Lawrence' and 'PreProject' in plans_selected[0]:
                LakeSL_prob_1D = True
                continue

            df_PI = yearly_timeseries_data_prep_map(ts_code, unique_pi_module_name, folder, PI_code, plans_selected,
                                                    Baseline, s, start_year, end_year, Variable, CFG_DASHBOARD, sas_token, container_url)

        else:
            LakeSL_prob_1D = False
            df_PI = yearly_timeseries_data_prep_map(ts_code, unique_pi_module_name, folder, PI_code, plans_selected,
                                                    Baseline, s,
                                                    start_year, end_year, Variable, CFG_DASHBOARD, sas_token, container_url)

        df_PI = df_PI.loc[df_PI['ALT'] == scen_code]

        multiplier = unique_PI_CFG.multiplier
        gdf_grille_unique = prep_data_map_1d(start_year, end_year, stat, gdf_grille_origin, s, df_PI, Variable,
                                             multiplier)
        gdfs.append(gdf_grille_unique)

    gdf_grille_all = pd.concat(gdfs)
    gdf_grille_all = gdf_grille_all.loc[gdf_grille_all['VAL'] != 0]
    gdf_grille_all = gdf_grille_all.dissolve(by='SECTION', as_index=False)

    gdf_grille_all['VAL'] = gdf_grille_all['VAL'] * multiplier

    return gdf_grille_all

def prep_data_map_1d(start_year, end_year, stat, gdf_grille_origine, s, df_PI, Variable, multiplier):
    print('PREP_DATA_MAP')
    df = df_PI
    df = df.loc[(df['YEAR'] >= start_year) & (df['YEAR'] <= end_year)]
    if stat == 'min':
        val = df[Variable].min()
    elif stat == 'max':
        val = df[Variable].max()
    elif stat == 'mean':
        val = df[Variable].mean()
    elif stat == 'sum':
        val = df[Variable].sum()
    else:
        print('unavailable aggregation stat provided')
    val = val * multiplier
    val = np.round(val, 3)
    gdf_grille = gdf_grille_origine

    gdf_grille['VAL'].loc[gdf_grille['SECTION'] == s] = val

    return gdf_grille

def yearly_timeseries_data_prep_map(ts_code, unique_pi_module_name, folder_raw, PI_code, plans_selected, Baseline,
                                    Region,
                                    start_year, end_year, Variable, CFG_DASHBOARD, sas_token, container_url):
    print('TIMESERIES_PREP')

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_folder = os.path.join(folder_raw, PI_code, 'YEAR', 'SECTION')
    dfs = []
    feather_done = []

    plans_all = plans_selected

    for p in plans_all:

        if p == Baseline:

            alt = unique_PI_CFG.baseline_dct[p]

        else:
            alt = unique_PI_CFG.plan_dct[p]
        sect = unique_PI_CFG.sect_dct[Region]

        if 'PreProject' in p:
            sect = [item for item in sect if item != "USL_DS"]

        for s in sect:

            if ts_code == 'hist':
                feather_name = f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years_hist)}_{np.max(unique_PI_CFG.available_years_hist)}{CFG_DASHBOARD.file_ext}'
            else:
                feather_name = f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years_future)}_{np.max(unique_PI_CFG.available_years_future)}{CFG_DASHBOARD.file_ext}'

            if feather_name not in feather_done:
                # if CFG_DASHBOARD.file_ext == '.feather':
                #     df = pd.read_feather(os.path.join(df_folder, alt, s, feather_name))
                # else:
                #     df = pd.read_csv(os.path.join(df_folder, alt, s, feather_name), sep=';')

                filepath = os.path.join(df_folder, alt, s, feather_name)

                filepath=filepath.replace('\\', '/')

                print(f'FILEPATH, {filepath}')

                file_url = f"{container_url}/{filepath}?{sas_token}"

                #df = read_from_sftp(filepath, sftp)

                df=pd.read_parquet(file_url)

                df['ALT'] = alt
                df['SECT'] = s

                dfs.append(df)
                # to make sure that a same feather is not compiled more than once in the results
                feather_done.append(feather_name)

    df_PI = pd.concat(dfs, ignore_index=True)
    df_PI = df_PI.loc[(df_PI['YEAR'] >= start_year) & (df_PI['YEAR'] <= end_year)]
    df_PI = df_PI.loc[df_PI['SECT'].isin(unique_PI_CFG.sect_dct[Region])]

    # for regions that include more than one section (ex. Canada inludes LKO_CAN and USL_CAN but we want only one value per year)
    var = [k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]

    stats = unique_PI_CFG.var_agg_stat[var]

    df_PI['SECT'] = Region
    # when a variable can be aggregated by mean or sum, sum is done in priority
    if len(stats) > 1:
        df_PI = df_PI[['YEAR', 'ALT', 'SECT', f'{var}_sum']]
        df_PI = df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).sum()
    elif stats[0] == 'sum':
        df_PI = df_PI[['YEAR', 'ALT', 'SECT', f'{var}_sum']]
        df_PI = df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).sum()
    elif stats[0] == 'mean':
        df_PI = df_PI[['YEAR', 'ALT', 'SECT', f'{var}_mean']]
        df_PI = df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).mean()
    else:
        print('problem w. agg stat!!')

    df_PI[Variable] = df_PI[f'{var}_{stats[0]}']

    multiplier = unique_PI_CFG.multiplier
    df_PI[Variable] = df_PI[Variable] * multiplier

    df_PI = df_PI[['YEAR', 'ALT', 'SECT', Variable]]

    return df_PI


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
            print(os.listdir(tmpdirname))
            for file_name in os.listdir(tmpdirname):
                file_path = os.path.join(tmpdirname, file_name)
                zip_file.write(file_path, arcname=file_name)

        # Move the pointer to the beginning of the buffer
        zip_buffer.seek(0)

        return zip_buffer.getvalue()

def create_folium_dual_map(_gdf_grille_base, _gdf_grille_plan, col, var, unique_pi_module_name, unit, division_col):
    print('DUAL_MAPS')
    geometry_types = _gdf_grille_base.geom_type.unique()[0]

    if geometry_types == 'MultiPolygon' or geometry_types == 'Polygon':
        x_med = np.round(_gdf_grille_base.geometry.centroid.x.median(), 3)
        y_med = np.round(_gdf_grille_base.geometry.centroid.y.median(), 3)
    else:
        x_med = np.round(_gdf_grille_base.geometry.x.median(), 3)
        y_med = np.round(_gdf_grille_base.geometry.y.median(), 3)

    m = plugins.DualMap(location=(y_med, x_med), tiles='cartodbpositron', zoom_start=8)

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    direction = unique_PI_CFG.var_direction[var]

    gdf_grille_1 = _gdf_grille_base.copy(deep=True)

    if 'NFB' in unique_pi_module_name:
        gdf_grille_1[col] = gdf_grille_1[col].astype(int).round(3)
        gdf_grille_1 = gdf_grille_1.loc[gdf_grille_1[col] != 1]
    else:
        gdf_grille_1[col] = gdf_grille_1[col].astype(float).round(3)

    if direction == 'inverse':
        linear = cm.LinearColormap(["darkgreen", "green", "lightblue", "orange", "red"],
                                   vmin=gdf_grille_1[col].quantile(0.25), vmax=gdf_grille_1[col].quantile(0.75),
                                   caption=unit)
    else:
        linear = cm.LinearColormap(["red", "orange", "lightblue", "green", "darkgreen"],
                                   vmin=gdf_grille_1[col].quantile(0.25), vmax=gdf_grille_1[col].quantile(0.75),
                                   caption=unit)

    linear.add_to(m.m1)

    if division_col != 'SECTION':
        gdf_grille_1[division_col] = gdf_grille_1[division_col].astype(int)

    val_dict = gdf_grille_1.set_index(division_col)[col]

    centro = gdf_grille_1.copy(deep=True)

    gdf_grille_1 = gdf_grille_1.to_crs(epsg='4326')

    centro['centroid'] = centro.centroid
    centro['centroid'] = centro["centroid"].to_crs(epsg=4326)

    gjson = gdf_grille_1.to_json()

    if division_col == 'SECTION':
        folium.GeoJson(
            gjson,
            style_function=lambda feature: {
                "fillColor": linear(val_dict[feature["properties"][division_col]]),
                "color": "black",
                "weight": 2,
                "dashArray": "5, 5",
            },
        ).add_to(m.m1)

        for _, r in centro.iterrows():
            lat = r["centroid"].y
            lon = r["centroid"].x
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    html=f"""<div style="font-family: courier new; color: black; font-size:20px; font-weight:bold">{r[col]}</div>""")
            ).add_to(m.m1)
    else:
        tooltip = folium.GeoJsonTooltip(
            fields=['tile', col],
            aliases=['Tile', var],
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
            fields=["tile", col],
            aliases=["tile", var],
            localize=True,
            labels=True,
            style="background-color: yellow;",
        )

        folium.GeoJson(
            gjson,
            style_function=lambda feature: {
                "fillColor": linear(val_dict[feature["properties"][division_col]]),
                "color": "black",
                "fillOpacity": 0.4,
            },
            tooltip=tooltip,
            popup=popup
        ).add_to(m.m1)

    ######

    gdf_grille_2 = _gdf_grille_plan.copy(deep=True)
    gdf_grille_2[col] = gdf_grille_2[col].astype(float)

    val_dict2 = gdf_grille_2.set_index(division_col)[col]

    centro = gdf_grille_2.copy(deep=True)

    gdf_grille_2 = gdf_grille_2.to_crs(epsg='4326')

    centro['centroid'] = centro.centroid
    centro['centroid'] = centro["centroid"].to_crs(epsg=4326)

    gjson = gdf_grille_2.to_json()
    val_dict2 = gdf_grille_2.set_index(division_col)[col]

    if division_col == 'SECTION':
        folium.GeoJson(
            gjson,
            style_function=lambda feature: {
                "fillColor": linear(val_dict2[feature["properties"][division_col]]),
                "color": "black",
                "weight": 2,
                "dashArray": "5, 5",
            },
        ).add_to(m.m2)

        for _, r in centro.iterrows():
            lat = r["centroid"].y
            lon = r["centroid"].x
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    html=f"""<div style="font-family: courier new; color: black; font-size:20px; font-weight:bold">{r[col]}</div>""")
            ).add_to(m.m2)

    else:
        tooltip = folium.GeoJsonTooltip(
            fields=['tile', col],
            aliases=['Tile', var],
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
            fields=["tile", col],
            aliases=["tile", var],
            localize=True,
            labels=True,
            style="background-color: yellow;",
        )

        g = folium.GeoJson(
            gjson,
            style_function=lambda x: {
                "fillColor": linear(val_dict2[x["properties"][division_col]]),
                "color": "black",
                "fillOpacity": 0.4,
            },
            tooltip=tooltip,
            popup=popup
        ).add_to(m.m2)

    return m

def folium_static(_fig, width, height):
    print('FOLIUM_STATIC')

    if isinstance(_fig, folium.Map):
        _fig = folium.Figure().add_child(_fig)
        return components.html(
            _fig.render(), height=(_fig.height or height) + 10, width=width
        )

    elif isinstance(_fig, plugins.DualMap):
        return components.html(
            _fig._repr_html_(), height=height + 10, width=width)

def MAIN_FILTERS_streamlit_simple(ts_code, unique_pi_module_name, Years, Variable):
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

    return start_year, end_year, Variable