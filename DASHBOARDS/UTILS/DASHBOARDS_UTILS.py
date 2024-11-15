import os
import streamlit as st
import numpy as np
import importlib
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import branca.colormap as cm
import folium
from folium import plugins
import json
import streamlit.components.v1 as components
from DASHBOARDS.ISEE import CFG_ISEE_DASH as CFG_DASHBOARD
import tempfile
from streamlit_folium import st_folium


#@st.cache_data(ttl=3600)
def prep_data_map_1d(file, start_year, end_year, stat, var, gdf_grille_origine, s, var_stat, df_PI, Variable, multiplier):

    print('PREP_DATA_MAP')

    df=df_PI
    df=df.loc[(df['YEAR']>=start_year) & (df['YEAR']<=end_year)]

    if stat=='Min':
        val=df[Variable].min()
    elif stat=='Max':
        val=df[Variable].max()
    elif stat=='mean':
        val=df[Variable].mean()
    elif stat=='sum':
        val=df[Variable].sum()
    else:
        print('unavailable aggregation stat provided')

    val=val*multiplier
    val=np.round(val, 3)
    gdf_grille=gdf_grille_origine

    # gdf_grille['VAL'].loc[gdf_grille['SECTION'].isin(sct_map_dct[s])]=val
    gdf_grille['VAL'].loc[gdf_grille['SECTION']==s]=val

    return gdf_grille

#@st.cache_data(ttl=3600)
def prep_for_prep_1d(sect_dct, sct_poly, folder, PI_code, scen_code, avail_years, stat, var, unique_pi_module_name, start_year, end_year, Baseline):
    print('PREP_FOR_PREP_1D')

    gdf_grille_origin=gpd.read_file(sct_poly)
    gdf_grille_origin['VAL']=0.0
    
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    var_stat=unique_PI_CFG.var_agg_stat[var][0]
    gdfs=[]
    
    list_sect=sect_dct.keys()
    
    for s in list_sect:
        df_folder=os.path.join(folder, PI_code, 'YEAR', 'SECTION',  scen_code, s)
        pt_id_file=os.path.join(df_folder, f'{PI_code}_YEAR_{scen_code}_{s}_{np.min(avail_years)}_{np.max(avail_years)}{CFG_DASHBOARD.file_ext}')
        
        plans_selected=[key for key,value in unique_PI_CFG.plan_dct.items() if value == scen_code]
        if plans_selected==[]:
            plans_selected=[key for key,value in unique_PI_CFG.baseline_dct.items() if value == scen_code]
        Variable=unique_PI_CFG.dct_var[var]      

        if s=='Lake St.Lawrence':

            LakeSL_prob_1D =False
            if unique_PI_CFG.type=='1D'and s=='Lake St.Lawrence' and plans_selected[0]=='PreProjectHistorical':
                LakeSL_prob_1D=True
                continue

            df_PI=yearly_timeseries_data_prep_map(unique_pi_module_name, folder, PI_code, plans_selected, Baseline, s, start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D)

        else:
            LakeSL_prob_1D = False
            df_PI = yearly_timeseries_data_prep_map(unique_pi_module_name, folder, PI_code, plans_selected, Baseline, s,
                                                    start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D)

        df_PI = df_PI.loc[df_PI['ALT']==scen_code]

        multiplier=unique_PI_CFG.multiplier
        gdf_grille_unique=prep_data_map_1d(pt_id_file, start_year, end_year, stat, var, gdf_grille_origin, s, var_stat, df_PI, Variable, multiplier)
        
        gdf_grille_unique.to_file(fr'{CFG_DASHBOARD.debug_folder}\{PI_code}_{scen_code}_{s}.shp')
        gdfs.append(gdf_grille_unique)
        
    gdf_grille_all=pd.concat(gdfs)
    gdf_grille_all=gdf_grille_all.loc[gdf_grille_all['VAL']!=0]
    gdf_grille_all=gdf_grille_all.dissolve(by='SECTION', as_index=False)
    return gdf_grille_all


def prep_for_prep_tiles(tile_shp, folder, PI_code, scen_code, avail_years, stat, var,
                        unique_pi_module_name, start_year, end_year):
    print('PREP_FOR_PREP_TILES')

    gdf_tiles = gpd.read_file(tile_shp)
    gdf_tiles['VAL'] = np.nan

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    var_stat = unique_PI_CFG.var_agg_stat[var][0]
    sect_PI = unique_PI_CFG.available_sections
    gdfs = []

    for s in sect_PI:

        liste_tiles = CFG_DASHBOARD.dct_tile_sect[s]

        for t in liste_tiles:

            df_folder = os.path.join(folder, PI_code, 'YEAR', 'TILE', scen_code, s, str(t))
            pt_id_file = os.path.join(df_folder,
                                      f'{PI_code}_YEAR_{scen_code}_{s}_{str(t)}_{np.min(avail_years)}_{np.max(avail_years)}{CFG_DASHBOARD.file_ext}')
            if not os.path.exists(pt_id_file):
                continue
            df_tile = pd.read_feather(pt_id_file)

            df_tile = df_tile.loc[(df_tile['YEAR'] >= start_year) & (df_tile['YEAR'] <= end_year)]

            multiplier = unique_PI_CFG.multiplier

            if f'{var}_mean' in list(df_tile):

                val_mean = df_tile[f'{var}_mean'].mean()* multiplier
                val_sum = df_tile[f'{var}_mean'].sum()* multiplier
                val_min = df_tile[f'{var}_mean'].min()* multiplier
                val_max = df_tile[f'{var}_mean'].max()* multiplier

            elif f'{var}_sum' in list(df_tile):
                val_mean = df_tile[f'{var}_sum'].mean()* multiplier
                val_sum = df_tile[f'{var}_sum'].sum()* multiplier
                val_min = df_tile[f'{var}_sum'].min()* multiplier
                val_max = df_tile[f'{var}_sum'].max()* multiplier

            else:
                print('problem with stats')

            gdf_tiles.loc[gdf_tiles['tile'] == t, 'VAL_MEAN'] = round(val_mean, 3)
            gdf_tiles.loc[gdf_tiles['tile'] == t, 'VAL_SUM'] = round(val_sum, 3)
            gdf_tiles.loc[gdf_tiles['tile'] == t, 'VAL_MIN'] = round(val_min, 3)
            gdf_tiles.loc[gdf_tiles['tile'] == t, 'VAL_MAX'] = round(val_max, 3)

    gdf_tiles = gdf_tiles.dropna(subset=["VAL_MEAN", 'VAL_SUM', 'VAL_MIN', 'VAL_MAX'])

    if stat == 'mean':
        gdf_tiles['VAL'] = gdf_tiles['VAL_MEAN']
    elif stat == 'sum':
        gdf_tiles['VAL'] = gdf_tiles['VAL_SUM']
    elif stat == 'min':
        gdf_tiles['VAL'] = gdf_tiles['VAL_MIN']
    elif stat == 'max':
        gdf_tiles['VAL'] = gdf_tiles['VAL_MAX']
    else:
        print('problem with stats')

    gdf_tiles=gdf_tiles.drop(columns=["VAL_MEAN", 'VAL_SUM', 'VAL_MIN', 'VAL_MAX'])

    return gdf_tiles

@st.cache_data(ttl=3600)
def header(selected_pi, Stats, PIs, start_year, end_year, Region, plans_selected, Baseline, max_plans, plan_values, baseline_value, PI_code, unit_dct,  var_direction, LakeSL_prob_1D):

    print('HEADER')

    if var_direction=='inverse':
        delta_color='inverse'
    else:
        delta_color='normal'
    
    plan_values=list(map(float, plan_values))
    baseline_value=float(baseline_value)

    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(f':blue[{Stats}] of :blue[{selected_pi}] from :blue[{start_year} to {end_year}], in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')
    placeholder2 = st.empty()
    with placeholder2.container():   
        kpis = st.columns(max_plans+1)
        count_kpi=1
        while count_kpi <= len(plans_selected)+1:
            d=count_kpi-1
            if count_kpi!=len(plans_selected)+1:
                if LakeSL_prob_1D:
                    kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit_dct[PI_code]})', value=round(plan_values[d], 2), delta=0)
                else:
                    kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit_dct[PI_code]})',
                                   value=round(plan_values[d], 2),
                                   delta=round(round(plan_values[d], 2) - round(baseline_value, 2), 2),
                                   delta_color=delta_color)
            else:
                kpis[d].metric(label=fr':green[Reference plan {Stats} ({unit_dct[PI_code]})]', value=round(baseline_value, 2), delta= 0)
            count_kpi+=1

def create_folium_dual_map(_gdf_grille_base, _gdf_grille_plan, col, dim_x, dim_y, var, type, unique_pi_module_name, unit, division_col):

    print('DUAL_MAPS')
    geometry_types = _gdf_grille_base.geom_type.unique()[0]

    if geometry_types == 'MultiPolygon' or geometry_types == 'Polygon':
        x_med=np.round(_gdf_grille_base.geometry.centroid.x.median(), 3)
        y_med=np.round(_gdf_grille_base.geometry.centroid.y.median(), 3)
    else:
        x_med = np.round(_gdf_grille_base.geometry.x.median(), 3)
        y_med = np.round(_gdf_grille_base.geometry.y.median(), 3)

    m = plugins.DualMap(location=(y_med, x_med), tiles='cartodbpositron', zoom_start=8)

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    direction = unique_PI_CFG.var_direction[var]

    gdf_grille_1 = _gdf_grille_base.copy(deep=True)

    if 'NFB' in unique_pi_module_name:
        gdf_grille_1[col] = gdf_grille_1[col].astype(int).round(3)
        gdf_grille_1=gdf_grille_1.loc[gdf_grille_1[col] != 1]
    else:
        gdf_grille_1[col] = gdf_grille_1[col].astype(float).round(3)

    if direction == 'inverse':
        linear = cm.LinearColormap(["darkgreen", "green", "lightblue", "orange", "red"],
                                   vmin=gdf_grille_1[col].quantile(0.25), vmax=gdf_grille_1[col].quantile(0.75), caption=unit)

    else:
        linear = cm.LinearColormap(["red", "orange", "lightblue", "green", "darkgreen"],
                                   vmin=gdf_grille_1[col].quantile(0.25), vmax=gdf_grille_1[col].quantile(0.75), caption=unit)

    linear.add_to(m.m1)

    if division_col != 'SECTION':
        gdf_grille_1[division_col] = gdf_grille_1[division_col].astype(int)

    val_dict = gdf_grille_1.set_index(division_col)[col]

    centro = gdf_grille_1.copy(deep=True)

    gdf_grille_1 = gdf_grille_1.to_crs(epsg='4326')

    centro['centroid'] = centro.centroid
    centro['centroid'] = centro["centroid"].to_crs(epsg=4326)

    gjson = gdf_grille_1.to_json()
    js_data = json.loads(gjson)

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
    js_data = json.loads(gjson)
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

#@st.cache_data(ttl=3600)
def create_folium_map(gdf_grille, col, dim_x, dim_y, var, type, unique_pi_module_name, unit, division_col):

    print('FOLIUM_MAPS')

    geometry_types = gdf_grille.geom_type.unique()[0]

    if geometry_types == 'MultiPolygon' or geometry_types == 'Polygon':
        x_med=np.round(gdf_grille.geometry.centroid.x.median(), 3)
        y_med=np.round(gdf_grille.geometry.centroid.y.median(), 3)
    else:
        x_med = np.round(gdf_grille.geometry.x.median(), 3)
        y_med = np.round(gdf_grille.geometry.y.median(), 3)

    folium_map = folium.Map(location=[y_med, x_med], zoom_start=8, tiles='cartodbpositron', height=dim_y, width=dim_x)

    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    
    direction=unique_PI_CFG.var_direction[var]
           
    gdf_grille[col]=gdf_grille[col].astype(float)
    
    if type=='diff':
        if direction == 'inverse':
            linear = cm.LinearColormap(colors=['green', 'white', 'red'], index=[gdf_grille[col].quantile(0.25), 0, gdf_grille[col].quantile(0.75)], vmin=gdf_grille[col].quantile(0.25),
                                         vmax=gdf_grille[col].quantile(0.75))

        else:
            linear = cm.LinearColormap(colors=['red', 'white', 'green'], index=[gdf_grille[col].quantile(0.25), 0, gdf_grille[col].quantile(0.75)], vmin=gdf_grille[col].quantile(0.25),
                                    vmax=gdf_grille[col].quantile(0.75))

    else:
        if direction == 'inverse':
            linear = cm.LinearColormap(["darkgreen", "green", "lightblue", "orange", "red"], vmin=gdf_grille[col].quantile(0.25), vmax=gdf_grille[col].quantile(0.75), caption=unit)

        else:
            linear = cm.LinearColormap(["red", "orange", "lightblue", "green", "darkgreen"], vmin=gdf_grille[col].quantile(0.25), vmax=gdf_grille[col].quantile(0.75), caption=unit)

    val_dict = gdf_grille.set_index(division_col)[col]

    centro=gdf_grille.copy(deep=True)

    gdf_grille=gdf_grille.to_crs(epsg='4326')

    gdf_grille= gdf_grille.dropna()

    if division_col != 'SECTION':
        print(gdf_grille['tile'].unique())
    
    centro['centroid']=centro.centroid
    centro['centroid']=centro["centroid"].to_crs(epsg=4326)
    
    
    gjson = gdf_grille.to_json()
    js_data = json.loads(gjson)
    val_dict = gdf_grille.set_index(division_col)[col]

    if division_col == 'SECTION':
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
                icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: black; font-size:20px; font-weight:bold">{r[col]}</div>""")
                #popup="length: {} <br> area: {}".format(r["Shape_Leng"], r["Shape_Area"]),
            ).add_to(folium_map)

    else:
        tooltip = folium.GeoJsonTooltip(
            fields=['tile', col],
            aliases=['tile', var],
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
                "fillColor": linear(val_dict[x["properties"][division_col]]),
                "color": "black",
                "fillOpacity": 0.4,
            },
            tooltip=tooltip,
            popup=popup,
        ).add_to(folium_map)

    return folium_map

#@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
def prep_data_map(df, start_year, end_year, id_col, col_x, col_y, stat, Variable, unique_pi_module_name, pi_type, tile):

    print('PREP_DATA_MAP')
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

    df.fillna(0, inplace=True)
    
    liste_year=list(range(start_year, end_year+1))
    liste_year = [str(i) for i in liste_year]
    liste_year=[y for y in liste_year if y in list(df)]
    
    columns=[id_col, col_x, col_y] + liste_year
    df=df[columns]
    if stat=='min':
        df['stat']=df[liste_year].min(axis=1)
    if stat=='max':
        df['stat']=df[liste_year].max(axis=1)
    if stat=='mean':
        df['stat']=df[liste_year].mean(axis=1)
    if stat=='sum':
        df['stat']=df[liste_year].sum(axis=1)
        
    df['stat']=df['stat'].round(3)
    df[Variable]=df['stat']

    multiplier=unique_PI_CFG.multiplier
    df[Variable]= df[Variable]*multiplier

    df=df[[id_col, col_x, col_y, Variable]]
    df.dropna(subset=[Variable], inplace=True)
    
    return df

@st.cache_data(ttl=3600)
def plot_map_plotly(Variable, df, col_x, col_y, id_col, unique_pi_module_name, plan, col_value):

    print('PLOT_MAP_PLOTLY')
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    direction = unique_PI_CFG.var_direction[Variable]

    x_med = np.round(df[col_x].median(), 3)
    y_med = np.round(df[col_y].median(), 3)

    ### transforme les valeurs de hectares à metre carrés!
    if unique_PI_CFG.multiplier==0.01:
        df[col_value]=df[col_value]*10000

    df=df[['PT_ID', col_value, 'LAT', 'LON']]

    df[col_value]=df[col_value].astype(float)
    df[col_value] = df[col_value].round(3)
    df = df.dropna(subset=[col_value])

    df = df.loc[df[col_value]!=0]

    if len(df)>10000:
        size=7
    elif len(df)>1000:
        size=10
    else:
        size=12

    value_range = [df[col_value].min(), df[col_value].max()]
    df_neg=df.loc[df[col_value]<0]
    df_pos = df.loc[df[col_value] > 0]

    print(df_neg[col_value].unique())
    print(df_pos[col_value].unique())

    if len(df_neg[col_value].unique())==0 and len(df_pos[col_value].unique())==0:
        print(df_neg[col_value].unique())
        print(df_pos[col_value].unique())

        colormap1 = 'greens'
        colormap2 = 'greens'
        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]
        empty_map=True

    elif len(df_neg[col_value].unique())<5 or len(df_pos[col_value].unique())<5:
        if direction == 'normal':
            colormap1 = 'greens'
            colormap2 = 'reds_r'

        elif direction == 'inverse':
            colormap2 = 'greens_r'
            colormap1 = 'reds'

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]

        empty_map=False

    elif df_pos[col_value].quantile(0.25)==df_pos[col_value].quantile(0.75) or df_neg[col_value].quantile(0.25)==df_neg[col_value].quantile(0.75):
        if direction == 'normal':
            colormap1 = 'greens'
            colormap2 = 'reds_r'

        elif direction == 'inverse':
            colormap2 = 'greens_r'
            colormap1 = 'reds'

        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = df_pos[col_value]
        norm2 = df_neg[col_value]

        empty_map=False

    else:
        if direction == 'normal':
            colormap1 = [
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

            colormap2 = [
            [0, "#800000"],    # dark red
            [0.1, "#990000"],  # slightly lighter dark red
            [0.2, "#b30000"],  # lighter dark red
            [0.3, "#cc0000"],  # medium red
            [0.4, "#e60000"],  # medium-light red
            [0.5, "#ff1a1a"],  # light red
            [0.6, "#ff3333"],  # very light red
            [0.7, "#ff6666"],  # even lighter red
            [0.8, "#ff9999"],  # very light red
            [0.9, "#ffcccc"],  # almost white with a hint of red
            [1, "white"]       # white
        ]

        elif direction == 'inverse':
            colormap2 = [
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

            colormap1 = [
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



        else:
            print('There is a problem with variable direction!!')
            quit()

        norm1 = (df_pos[col_value] - df_pos[col_value].quantile(0.25)) / (df_pos[col_value].quantile(0.75) - df_pos[col_value].quantile(0.25))
        norm2 = (df_neg[col_value] - df_neg[col_value].quantile(0.25)) / (df_neg[col_value].quantile(0.75) - df_neg[col_value].quantile(0.25))

        empty_map = False

    print(df_pos[col_value].quantile(0.25), df_pos[col_value].quantile(0.75))
    print(df_neg[col_value].quantile(0.25), df_neg[col_value].quantile(0.75))

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
    lat = df_neg[col_y],
    lon = df_neg[col_x],
    mode = 'markers',
    marker = go.scattermapbox.Marker(
    size = size,
        color=norm2,
        colorscale=colormap2,
        cmin=0,
        cmax=1,
        opacity=1
    ),
    text = df_neg[col_value],
    hoverinfo = 'text',

    )

    fig = go.Figure(data=[trace1, trace2])

    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ],  mapbox=dict(
            style='open-street-map',
            center=dict(lat=y_med, lon=x_med),
            zoom=13
        ))


    fig.update_traces(
        marker=dict(sizemode='area', sizeref=2, sizemin=2)
        # Adjust sizeref and sizemin for smaller markers
    )

    coords_lat=df[col_y]

    coords_lon=df[col_x]

    coordinates = [[coords_lon.min(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.max()],
                   [coords_lon.min(), coords_lat.max()]]

    fig.update_layout(mapbox_layers=[{"coordinates": coordinates}],  autosize=True,
    margin=dict(l=0, r=0, t=0, b=0),
    height=1000)

    if empty_map:
        fig='empty'

    return fig

@st.cache_data(ttl=3600)
def plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct, unique_pi_module_name, diff_type):
    print('PLOT_DTS')
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    df_PI_plans['BASELINE_VALUE']=1.0
    
    for y in list(range(start_year, end_year+1)):
        for p in list_plans:

            ### WORKAROUND so if value is missing it still continues....
            if len(df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==unique_PI_CFG.baseline_dct[Baseline])])>0:
                df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==unique_PI_CFG.baseline_dct[Baseline])].iloc[0].round(3)
            else:
                df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = 0.000001
                
    df_PI_plans['DIFF_PROP']=((df_PI_plans[Variable]-df_PI_plans['BASELINE_VALUE'])/df_PI_plans['BASELINE_VALUE'])*100
    df_PI_plans['DIFF']=df_PI_plans[Variable]-df_PI_plans['BASELINE_VALUE']
    diff_dct={f'Values ({unit_dct[PI_code]})': 'DIFF', 'Proportion of reference value (%)': 'DIFF_PROP'}
    fig2=px.bar(df_PI_plans, x='YEAR', y=df_PI_plans[diff_dct[diff_type]], color='ALT', barmode='group', hover_data={'ALT': True, 'YEAR': True, diff_dct[diff_type]:True})
    fig2.update_layout(title=f'Difference between each selected plans and the reference for each year of the selected time period',
           xaxis_title='Years',
           yaxis_title=f'Difference in {diff_type}')
    
    return fig2

@st.cache_data(ttl=3600)
def plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, PI_code, unit_dct):

    print('PLOT_TS')

    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    fig = px.line(df_PI_plans, x="YEAR", y=Variable, color='ALT', labels={'ALT':'Plans'})
    fig['data'][-1]['line']['color']="#00ff00"
    fig['data'][-1]['line']['width']=3
    fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
           xaxis_title='Years',
           yaxis_title=f'{unit_dct[PI_code]}')
    return fig

@st.cache_data(ttl=3600)
def plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, unique_PI_CFG, LakeSL_prob_1D):

    print('PLAN AGRREGATED')
    multiplier = unique_PI_CFG.multiplier
    if LakeSL_prob_1D:
        baseline_value=0

        if Stats == 'mean':
            plan_values = []
            for c in range(len(plans_selected)):
                plan_value = df_PI[Variable].loc[
                    df_PI['ALT'] == unique_PI_CFG.plan_dct[plans_selected[c]]].mean().round(3)
                plan_value = plan_value * multiplier
                plan_values.append(plan_value)

        if Stats == 'sum':
            plan_values = []
            for c in range(len(plans_selected)):
                plan_value = df_PI[Variable].loc[df_PI['ALT'] == unique_PI_CFG.plan_dct[plans_selected[c]]].sum().round(
                    3)
                plan_value = plan_value * multiplier
                plan_values.append(plan_value)


    else:
        if Stats == 'mean':
            plan_values=[]
            baseline_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.baseline_dct[Baseline]].mean().round(3)
            baseline_value = baseline_value * multiplier
            for c in range(len(plans_selected)):
                plan_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.plan_dct[plans_selected[c]]].mean().round(3)
                plan_value=plan_value*multiplier
                plan_values.append(plan_value)

        if Stats == 'sum':
            plan_values=[]
            baseline_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.baseline_dct[Baseline]].sum().round(3)
            baseline_value = baseline_value * multiplier
            for c in range(len(plans_selected)):
                plan_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.plan_dct[plans_selected[c]]].sum().round(3)
                plan_value = plan_value * multiplier
                plan_values.append(plan_value)

    return baseline_value, plan_values

@st.cache_data(ttl=3600)
def yearly_timeseries_data_prep(unique_pi_module_name, folder_raw, PI_code, plans_selected, Baseline, Region, start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D):
    print('TIMESERIES_PREP')

    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_folder=os.path.join(folder_raw, PI_code, 'YEAR', 'SECTION')
    dfs=[]
    feather_done=[]

    if LakeSL_prob_1D:
        plans_all=plans_selected
    else:
        plans_all = plans_selected + [Baseline]

    for p in plans_all:

        if p == Baseline:
            alt=unique_PI_CFG.baseline_dct[p]
        else:
            alt=unique_PI_CFG.plan_dct[p]
        sect=unique_PI_CFG.sect_dct[Region]
        for s in sect:
            feather_name=f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}{CFG_DASHBOARD.file_ext}'
            if feather_name not in feather_done:
                if CFG_DASHBOARD.file_ext =='.feather':
                    df=pd.read_feather(os.path.join(df_folder, alt, s, feather_name))
                else:
                    df=pd.read_csv(os.path.join(df_folder, alt, s, feather_name), sep=';')
                df['ALT']=alt
                df['SECT']=s

                dfs.append(df)
                #to make sure that a same feather is not compiled more than once in the results
                feather_done.append(feather_name)
                          
    df_PI=pd.concat(dfs, ignore_index=True)
    df_PI=df_PI.loc[(df_PI['YEAR']>=start_year) & (df_PI['YEAR']<=end_year)]
    df_PI=df_PI.loc[df_PI['SECT'].isin(unique_PI_CFG.sect_dct[Region])]

    # for regions that include more than one section (ex. Canada inludes LKO_CAN and USL_CAN but we want only one value per year)
    var=[k for k, v in unique_PI_CFG.dct_var.items() if v == Variable][0]
    
    stats=unique_PI_CFG.var_agg_stat[var]

    df_PI['SECT']=Region 
    # when a variable can be aggregated by mean or sum, sum is done in priority
    if len(stats)>1:
        df_PI=df_PI[['YEAR', 'ALT', 'SECT', f'{var}_sum']]
        df_PI=df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).sum()
    elif stats[0]=='sum':
        df_PI=df_PI[['YEAR', 'ALT', 'SECT', f'{var}_sum']]
        df_PI=df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).sum()
    elif stats[0]=='mean':
        df_PI=df_PI[['YEAR', 'ALT', 'SECT', f'{var}_mean']]
        df_PI=df_PI.groupby(by=['YEAR', 'ALT', 'SECT'], as_index=False).mean()
    else:
        print('problem w. agg stat!!')

    df_PI[Variable]=df_PI[f'{var}_{stats[0]}']

    multiplier=unique_PI_CFG.multiplier
    df_PI[Variable]=df_PI[Variable]*multiplier

    df_PI=df_PI[['YEAR', 'ALT', 'SECT', Variable]]
    
    return df_PI


@st.cache_data(ttl=3600)
def yearly_timeseries_data_prep_map(unique_pi_module_name, folder_raw, PI_code, plans_selected, Baseline, Region,
                                start_year, end_year, Variable, CFG_DASHBOARD, LakeSL_prob_1D):
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

        if  p == Baseline:
            sect = [item for item in sect if item != "USL_DS"]

        for s in sect:
            feather_name = f'{PI_code}_YEAR_{alt}_{s}_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}{CFG_DASHBOARD.file_ext}'
            if feather_name not in feather_done:
                if CFG_DASHBOARD.file_ext == '.feather':
                    df = pd.read_feather(os.path.join(df_folder, alt, s, feather_name))
                else:
                    df = pd.read_csv(os.path.join(df_folder, alt, s, feather_name), sep=';')
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

    # unique_PI_CFG.dct_var.items()

    df_PI[Variable] = df_PI[f'{var}_{stats[0]}']

    multiplier = unique_PI_CFG.multiplier
    df_PI[Variable] = df_PI[Variable] * multiplier

    df_PI = df_PI[['YEAR', 'ALT', 'SECT', Variable]]

    return df_PI


def MAIN_FILTERS_streamlit(unique_pi_module_name, CFG_DASHBOARD, Years, Region, Plans, Baselines, Stats, Variable):

    print('FILTERS')

    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    
    if Variable:
        available_variables=list(unique_PI_CFG.dct_var.values())
        Variable=st.selectbox("Select variable to display", available_variables, index=0)
    else:
        Variable='N/A'
      
    if Years:
        start_year, end_year=st.select_slider('Select a period', options=unique_PI_CFG.available_years, 
                                          value=(np.min(unique_PI_CFG.available_years), np.max(unique_PI_CFG.available_years)))
    else:
        start_year='N/A'
        end_year='N/A'
    
    if Region:
        available_sections=list(unique_PI_CFG.sect_dct.keys())
        Regions=st.selectbox("Select regions", available_sections)
        
    else:
        Regions='N/A'
  
    if Plans:
        available_plans=list(unique_PI_CFG.plan_dct.keys())
        plans_selected=st.multiselect('Regulation plans to compare', available_plans, max_selections=CFG_DASHBOARD.maximum_plan_to_compare, default=next(iter(available_plans)))
    else:
        plans_selected='N/A'
        
    if Baselines:
        baselines= list(unique_PI_CFG.baseline_dct.keys())
        Baseline=st.selectbox("Select a reference plan", baselines)
    else:
        Baseline='N/A'

    if Stats:
        var=[key for key,value in unique_PI_CFG.dct_var.items() if value == Variable][0]
        Stats=st.selectbox("Stats to compute", unique_PI_CFG.var_agg_stat[var])
    else:
        Stats='N/A'
    
    return  start_year, end_year, Regions, plans_selected, Baseline, Stats, Variable


def MAIN_FILTERS_streamlit_simple(unique_pi_module_name, CFG_DASHBOARD, Years, Region, Plans, Baselines, Stats, Variable):
    print('FILTERS')

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

    if Variable:
        available_variables = list(unique_PI_CFG.dct_var.values())
        Variable = st.selectbox("Select variable to display", available_variables, index=0)
    else:
        Variable = 'N/A'

    if Years:
        start_year, end_year = st.select_slider('Select a period', options=unique_PI_CFG.available_years,
                                                value=(np.min(unique_PI_CFG.available_years),
                                                       np.max(unique_PI_CFG.available_years)))
    else:
        start_year = 'N/A'
        end_year = 'N/A'

    return start_year, end_year, Variable