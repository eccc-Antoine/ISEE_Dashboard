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

from streamlit_folium import st_folium

def prep_data_map_1d(file, start_year, end_year, stat, var, gdf_grille_origine, sct_map_dct, s, var_stat, df_PI, Variable, multiplier):

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


def prep_for_prep_1d(sect_dct, sct_poly, folder, PI_code, scen_code, avail_years, stat, var, sct_map_dct, unique_pi_module_name, start_year, end_year, Baseline):

    gdf_grille_origin=gpd.read_file(sct_poly)
    gdf_grille_origin['VAL']=0.0
    
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    var_stat=unique_PI_CFG.var_agg_stat[var][0]
    #sect_PI=unique_PI_CFG.available_sections
    gdfs=[]
    
    list_sect=sect_dct.keys()
    
    for s in list_sect:
        #if s in sect_PI:
        df_folder=os.path.join(folder, PI_code, 'YEAR', 'SECTION',  scen_code, s)
        pt_id_file=os.path.join(df_folder, f'{PI_code}_YEAR_{scen_code}_{s}_{np.min(avail_years)}_{np.max(avail_years)}{CFG_DASHBOARD.file_ext}')
        
        plans_selected=[key for key,value in unique_PI_CFG.plan_dct.items() if value == scen_code]
        if plans_selected==[]:
            plans_selected=[key for key,value in unique_PI_CFG.baseline_dct.items() if value == scen_code]
        Variable=unique_PI_CFG.dct_var[var]      

        df_PI=yearly_timeseries_data_prep(unique_pi_module_name, folder, PI_code, plans_selected, Baseline, s, start_year, end_year, Variable, CFG_DASHBOARD)
        df_PI = df_PI.loc[df_PI['ALT']==scen_code]

        multiplier=unique_PI_CFG.multiplier
        gdf_grille_unique=prep_data_map_1d(pt_id_file, start_year, end_year, stat, var, gdf_grille_origin, sct_map_dct, s, var_stat, df_PI, Variable, multiplier)
        
        gdf_grille_unique.to_file(fr'H:\Projets\GLAM\Dashboard\debug\{PI_code}_{scen_code}_{s}.shp')
        gdfs.append(gdf_grille_unique)
        
    gdf_grille_all=pd.concat(gdfs)
    gdf_grille_all=gdf_grille_all.loc[gdf_grille_all['VAL']!=0]
    gdf_grille_all=gdf_grille_all.dissolve(by='SECTION', as_index=False)
    return gdf_grille_all

def prep_for_prep_tiles(tile_shp, folder, PI_code, scen_code, avail_years, stat, var,
                     unique_pi_module_name, start_year, end_year):
    gdf_tiles = gpd.read_file(tile_shp)
    gdf_tiles['VAL'] = np.nan

    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    var_stat = unique_PI_CFG.var_agg_stat[var][0]
    sect_PI=unique_PI_CFG.available_sections
    gdfs = []

    for s in sect_PI:

        liste_tiles=CFG_DASHBOARD.dct_tile_sect[s]

        for t in liste_tiles:

        # if s in sect_PI:
            df_folder = os.path.join(folder, PI_code, 'YEAR', 'TILE', scen_code, s, str(t))
            pt_id_file = os.path.join(df_folder,
                                      f'{PI_code}_YEAR_{scen_code}_{s}_{str(t)}_{np.min(avail_years)}_{np.max(avail_years)}{CFG_DASHBOARD.file_ext}')
            if not os.path.exists(pt_id_file):
                continue
            df_tile=pd.read_feather(pt_id_file)
            #print(list(df_tile))
            plans_selected = [key for key, value in unique_PI_CFG.plan_dct.items() if value == scen_code]
            if plans_selected == []:
                plans_selected = [key for key, value in unique_PI_CFG.baseline_dct.items() if value == scen_code]

            df_tile = df_tile.loc[(df_tile['YEAR'] >= start_year) & (df_tile['YEAR'] <= end_year)]

            if stat == 'mean':
                val = df_tile[f'{var}_{stat}'].mean()
            elif stat == 'sum':
                val = df_tile[f'{var}_{stat}'].sum()

            multiplier = unique_PI_CFG.multiplier
            val=val*multiplier
            gdf_tiles.loc[gdf_tiles['tile']==t, 'VAL']=val.round(3)

    gdf_tiles = gdf_tiles.dropna(subset=["VAL"])
    return gdf_tiles

def header(Stats, PIs, start_year, end_year, Region, plans_selected, Baseline, max_plans, plan_values, baseline_value, PI_code, unit_dct,  var_direction):
    
    if var_direction=='inverse':
        delta_color='inverse'
    else:
        delta_color='normal'
    
    plan_values=list(map(float, plan_values))
    baseline_value=float(baseline_value)
    
    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(f'Now showing :blue[{Stats}] of :blue[{PIs}], during :blue[{start_year} to {end_year}] period, in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')
    placeholder2 = st.empty()
    with placeholder2.container():   
        kpis = st.columns(max_plans+1)
        count_kpi=1
        while count_kpi <= len(plans_selected)+1:
            d=count_kpi-1
            if count_kpi!=len(plans_selected)+1:
                kpis[d].metric(label=fr'{plans_selected[d]} {Stats} ({unit_dct[PI_code]})', value=round(plan_values[d], 2), delta= round(round(plan_values[d], 2) -round(baseline_value, 2), 2), delta_color=delta_color)
            else:
                kpis[d].metric(label=fr':green[Reference plan {Stats} ({unit_dct[PI_code]})]', value=round(baseline_value, 2), delta= 0)
            count_kpi+=1

# def popup_html(z, col, plan, stat, var, type):
#     #sect_id=f'Section: {z["properties"]["SECTION"]}'
#     #val=f'Value: {z["properties"][col]}'
#     if type == 'diff':
#         text=f'Difference of {stat} {var} in {z["properties"]["SECTION"]} under {plan} compared to Reference Plan is {z["properties"][col]}'
#     else:
#         text=f'{stat} of {var} in {z["properties"]["SECTION"]} under {plan} is {z["properties"][col]}'
#     html = """
#     <!DOCTYPE html>
#     <html>
#     <center><p> """ + text + """ </p></center>
#     </html>
#     """
#     return html

def create_folium_dual_map(gdf_grille_base, gdf_grille_plan, col, dim_x, dim_y, var, type, unique_pi_module_name, unit, division_col):

    geometry_types = gdf_grille_base.geom_type.unique()[0]

    if geometry_types == 'MultiPolygon' or geometry_types == 'Polygon':
        x_med=np.round(gdf_grille_base.geometry.centroid.x.median(), 3)
        y_med=np.round(gdf_grille_base.geometry.centroid.y.median(), 3)
    else:
        x_med = np.round(gdf_grille_base.geometry.x.median(), 3)
        y_med = np.round(gdf_grille_base.geometry.y.median(), 3)


    m = plugins.DualMap(location=(y_med, x_med), tiles='cartodbpositron', zoom_start=8)
    #m1=folium.Map(location=[y_med, x_med], tiles='cartodbpositron', zoom_start=8, control_scale=True)
    #m2=folium.Map(location=[y_med, x_med], tiles='cartodbpositron', zoom_start=8, control_scale=True)



    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    direction = unique_PI_CFG.var_direction[var]

    gdf_grille_1 = gdf_grille_base.copy(deep=True)

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

    gdf_grille_1[division_col] = gdf_grille_1[division_col].astype(int)

    print(gdf_grille_1.dtypes)

    print(gdf_grille_1.head())
    print(gdf_grille_1['tile'].unique())

    tiles=gdf_grille_1['tile'].unique()
    if 375 in tiles:
        print(gdf_grille_1.loc[gdf_grille_1['tile']==375])
    if 176 in tiles:
        print(gdf_grille_1.loc[gdf_grille_1['tile'] == 176])



    val_dict = gdf_grille_1.set_index(division_col)[col]

    centro = gdf_grille_1.copy(deep=True)

    gdf_grille_1 = gdf_grille_1.to_crs(epsg='4326')

    #gdf_grille_1.to_file(r'C:\GLAM\Dashboard\debug\test.shp')

    centro['centroid'] = centro.centroid
    centro['centroid'] = centro["centroid"].to_crs(epsg=4326)

    gjson = gdf_grille_1.to_json()
    js_data = json.loads(gjson)
    val_dict = gdf_grille_1.set_index(division_col)[col]

    if division_col == 'SECTION':
        folium.GeoJson(
            gjson,
            style_function=lambda feature: {
                "fillColor": linear(val_dict[feature["properties"][division_col]]),
                "color": "black",
                "weight": 2,
                "dashArray": "5, 5",
            },
        ).add_to(m1)

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
            fields=["tile"],
            aliases=["tile"],
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
            popup=popup
        ).add_to(m.m1)


        
    ######
    
    gdf_grille_2 = gdf_grille_plan.copy(deep=True)
    gdf_grille_2[col] = gdf_grille_2[col].astype(float)

    val_dict = gdf_grille_2.set_index(division_col)[col]

    centro = gdf_grille_2.copy(deep=True)

    gdf_grille_2 = gdf_grille_2.to_crs(epsg='4326')

    centro['centroid'] = centro.centroid
    centro['centroid'] = centro["centroid"].to_crs(epsg=4326)

    gjson = gdf_grille_2.to_json()
    js_data = json.loads(gjson)
    val_dict = gdf_grille_2.set_index(division_col)[col]

    if division_col == 'SECTION':
        folium.GeoJson(
            gjson,
            style_function=lambda feature: {
                "fillColor": linear(val_dict[feature["properties"][division_col]]),
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
            fields=["tile"],
            aliases=["tile"],
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
            popup=popup
        ).add_to(m.m2)

    #click_data = st_folium(m.m1, height=dim_y, width=dim_x)
    #print(click_data)
    #if click_data and 'last_clicked' in click_data:
    #print(popup)
    #print(m.m1)
    # data = m.m1['last_object_clicked_popup']
    # if data != None:
    #     data=str(data)
    #     data = data.replace('tile', '')
    #     data = data.replace(' ', '')
    #     data = data.replace('\n', '')
    #     data=int(data)
    # else:
    #     data = 'please select a tile'
    #
    # # else:
    # #     data='please select a tile'
    #
    # st.write(data)

    # def get_pos(tile):
    #     return tile
    #
    #
    # data = None
    # data = get_pos(m['last_clicked']['tile'])
    # print(data)
    # if m.m1.get("last_clicked"):
    #     data = get_pos(m.m1["last_clicked"]["tile"])
    # if data is not None:
    #     st.write(data)
    # data = None
    # if m.get("last_clicked"):
    #     data = get_pos(m["last_clicked"]["tile"])
    #
    # click_data = st_folium(m, key="map")
    # print(click_data)
    #
    # if click_data and 'last_clicked' in click_data:
    #     data = click_data['last_clicked']['tile']
    # else:
    #     data=None

    #m.m1.add_child(folium.LatLngPopup())

    # click_data = st_folium(m, key="m")
    # if click_data and 'last_clicked' in click_data:
    #     data = click_data['last_clicked']
    #
    #
    # folium_static(m, dim_x, dim_y)

    return m

def create_folium_map(gdf_grille, col, dim_x, dim_y, var, type, unique_pi_module_name, unit, division_col):
    geometry_types = gdf_grille.geom_type.unique()[0]

    if geometry_types == 'MultiPolygon' or geometry_types == 'Polygon':
        x_med=np.round(gdf_grille.geometry.centroid.x.median(), 3)
        y_med=np.round(gdf_grille.geometry.centroid.y.median(), 3)
    else:
        x_med = np.round(gdf_grille.geometry.x.median(), 3)
        y_med = np.round(gdf_grille.geometry.y.median(), 3)

    folium_map = folium.Map(location=[y_med, x_med], zoom_start=8, tiles='cartodbpositron', height=dim_y, width=dim_x)

    #folium_map = st_folium(location=[y_med, x_med], zoom_start=8, tiles='cartodbpositron', height=dim_y, width=dim_x)

    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    
    direction=unique_PI_CFG.var_direction[var]
           
    gdf_grille[col]=gdf_grille[col].astype(float)
    
    if type=='diff':
        if direction == 'inverse':
            #linear = cm.StepColormap(["green", "red"], index=[-100000000000000, 0, 100000000000000000], caption=unit)
            linear = cm.LinearColormap(colors=['green', 'white', 'red'], index=[gdf_grille[col].quantile(0.25), 0, gdf_grille[col].quantile(0.75)], vmin=gdf_grille[col].quantile(0.25),
                                         vmax=gdf_grille[col].quantile(0.75))

        else:
            #linear = cm.StepColormap(["red", "green"], index=[-100000000000000, 0, 100000000000000000], caption=unit)
            linear = cm.LinearColormap(colors=['red', 'white', 'green'], index=[gdf_grille[col].quantile(0.25), 0, gdf_grille[col].quantile(0.75)], vmin=gdf_grille[col].quantile(0.25),
                                    vmax=gdf_grille[col].quantile(0.75))

        #linear.add_to(folium_map)
    else:
        if direction == 'inverse':
            linear = cm.LinearColormap(["darkgreen", "green", "lightblue", "orange", "red"], vmin=gdf_grille[col].quantile(0.25), vmax=gdf_grille[col].quantile(0.75), caption=unit)
            #step=linear.to_step(4)
        else:
            linear = cm.LinearColormap(["red", "orange", "lightblue", "green", "darkgreen"], vmin=gdf_grille[col].quantile(0.25), vmax=gdf_grille[col].quantile(0.75), caption=unit)
            #step=linear.to_step(4)
    #linear.add_to(folium_map)
    val_dict = gdf_grille.set_index(division_col)[col]

    centro=gdf_grille.copy(deep=True)

    gdf_grille=gdf_grille.to_crs(epsg='4326')

    gdf_grille= gdf_grille.dropna()

    print('NEW PLAN!!!!!!')
    print(gdf_grille.head())

    print(gdf_grille['tile'].unique())
    
    centro['centroid']=centro.centroid
    centro['centroid']=centro["centroid"].to_crs(epsg=4326)
    
    
    gjson = gdf_grille.to_json()
    js_data = json.loads(gjson)
    val_dict = gdf_grille.set_index(division_col)[col]

    print(val_dict)

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
            fields=[col],
            aliases=[var],
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
            fields=["tile"],
            aliases=["tile"],
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

    click_data = st_folium(folium_map, height=dim_y, width=dim_x)



    #linear.add_to(folium_map)
    #print(click_data)
    #
    data = click_data['last_object_clicked_popup']
    if data != None:
        data=str(data)
        data = data.replace('tile', '')
        data = data.replace(' ', '')
        data = data.replace('\n', '')
        data=int(data)


    else:
        data='please select a tile'

    #st.write(data)

    return data

    #folium_static(folium_map, dim_x, dim_y)


def folium_static(fig, width, height):
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)
        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width
            )
 
    elif isinstance(fig, plugins.DualMap):
        return components.html(
            fig._repr_html_(), height=height + 10, width=width)

def prep_data_map(file, start_year, end_year, id_col, col_x, col_y, stat, Variable, unique_pi_module_name):
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

    if CFG_DASHBOARD.file_ext =='.feather':
        df=pd.read_feather(file)
    else:
        df=pd.read_csv(file, sep=';')
    
    df.fillna(0, inplace=True)
    
    liste_year=list(range(start_year, end_year+1))
    liste_year = [str(i) for i in liste_year]
    liste_year=[y for y in liste_year if y in list(df)]
    
    columns=[id_col, col_x, col_y] + liste_year
    df=df[columns]
    if stat=='Min':
        df['stat']=df[liste_year].min(axis=1)
    if stat=='Max':
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

# def plot_map_folium(PIs, Variable, df, col_x, col_y, id_col, unique_pi_module_name, plan, col_value):
#     unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
#     direction = unique_PI_CFG.var_direction[Variable]
#     #print(Variable, direction)
#
#     x_med = np.round(df[col_x].median(), 3)
#     y_med = np.round(df[col_y].median(), 3)
#
#     unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
#
#     ### transforme les valeurs de hectares à metre carrés!
#     if unique_PI_CFG.multiplier==0.01:
#         df[col_value]=df[col_value]*10000
#
#     #df[col_value]=df[col_value].astype(int)
#     df = df.dropna(subset=[col_value])
#
#     df = df.loc[df[col_value]!=0]
#
#     m = folium.Map(location=[x_med, y_med], zoom_start=10)
#
#     marker_group = folium.FeatureGroup(name='Markers')
#
#     for _, row in df.iterrows():
#         folium.CircleMarker(
#             location=[row[col_y], row[col_x]],
#             radius=8,
#             popup=f"Value: {row[col_value]}",
#             color='blue',
#             fill=True,
#             fill_color='blue'
#         ).add_to(marker_group)
#
#     def add_marker(row):
#         folium.CircleMarker(
#             location=[row[col_y], row[col_x]],
#             radius=8,
#             popup=f"Value: {row[col_value]}",
#             color='blue',
#             fill=True,
#             fill_color='blue'
#         ).add_to(m)
#
#     marker_group.add_to(m)
#
#     #df.apply(add_marker, axis=1)
#
#     return m

def plot_map_plotly(PIs, Variable, df, col_x, col_y, id_col, unique_pi_module_name, plan, col_value):
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    direction = unique_PI_CFG.var_direction[Variable]
    print(Variable, direction)

    x_med = np.round(df[col_x].median(), 3)
    y_med = np.round(df[col_y].median(), 3)

    #unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')

    ### transforme les valeurs de hectares à metre carrés!
    if unique_PI_CFG.multiplier==0.01:
        df[col_value]=df[col_value]*10000

    df[col_value]=df[col_value].astype(int)
    df = df.dropna(subset=[col_value])

    df = df.loc[df[col_value]!=0]

    if len(df)>10000:
        size=4
    elif len(df)>1000:
        size=7
    else:
        size=10


    print(len(df))
    print(df.head())

    #gdf=gpd.GeoDataFrame(df, crs='4326', geometry=gpd.points_from_xy(df[col_x], df[col_y]))

    value_range = [df[col_value].min(), df[col_value].max()]

    # if direction == 'inverse':
    #     custom_diverging_colormap = [
    #         [0, 'rgb(0, 128, 0)'],  # Dark green
    #         [0.1, 'rgb(34, 139, 34)'],  # Forest green
    #         [0.2, 'rgb(0, 255, 0)'],  # Green
    #         [0.3, 'rgb(144, 238, 144)'],  # Light green
    #         [0.4, 'rgb(173, 255, 47)'],  # Yellow green
    #         [0.5, 'rgb(255, 255, 255)'],  # White
    #         [0.6, 'rgb(255, 160, 122)'],  # Light salmon
    #         [0.7, 'rgb(255, 99, 71)'],  # Tomato
    #         [0.8, 'rgb(255, 69, 0)'],  # Orange red
    #         [0.9, 'rgb(220, 20, 60)'],  # Crimson
    #         [1, 'rgb(255, 0, 0)']  # Red
    #     ]
    # else:
    #     custom_diverging_colormap = [
    #         [0, 'rgb(255, 0, 0)'],  # Red
    #         [0.1, 'rgb(220, 20, 60)'],  # Crimson
    #         [0.2, 'rgb(255, 69, 0)'],  # Orange red
    #         [0.3, 'rgb(255, 99, 71)'],  # Tomato
    #         [0.4, 'rgb(255, 160, 122)'],  # Light salmon
    #         [0.5, 'rgb(255, 255, 255)'],  # White
    #         [0.6, 'rgb(173, 255, 47)'],  # Yellow green
    #         [0.7, 'rgb(144, 238, 144)'],  # Light green
    #         [0.8, 'rgb(0, 255, 0)'],  # Green
    #         [0.9, 'rgb(34, 139, 34)'],  # Forest green
    #         [1, 'rgb(0, 128, 0)']  # Dark green
    #     ]

    df_neg=df.loc[df[col_value]<0]
    df_pos = df.loc[df[col_value] > 0]

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

    colormap2 = colormap2 = [
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

    norm1 = (df_pos[col_value] - df_pos[col_value].quantile(0.25)) / (df_pos[col_value].quantile(0.75) - df_pos[col_value].quantile(0.25))
    norm2 = (df_neg[col_value] - df_neg[col_value].quantile(0.25)) / (df_neg[col_value].quantile(0.75) - df_neg[col_value].quantile(0.25))

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
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=y_med, lon=x_med),
            zoom=13
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )


    # percentiles_neg = np.percentile(df.loc[df[col_value]<0, col_value], [0, 25, 50, 75, 100])
    # colors_neg = ['darkred', 'red', 'orange', 'yellow', 'lightyellow']
    #
    # print(percentiles_neg)
    #
    # percentiles_pos = np.percentile(df.loc[df[col_value]>0, col_value], [0, 25, 50, 75, 100])
    # colors_pos = ['lightgreen', 'green', 'lightblue', 'blue', 'darkblue']
    #
    # # Map values to colors based on percentiles
    # def get_color(value):
    #     if value < percentiles_neg[1]:
    #         return colors_neg[0]
    #     elif value <= percentiles_neg[2]:
    #         return colors_neg[1]
    #     elif value <= percentiles_neg[3]:
    #         return colors_neg[2]
    #     elif value <= percentiles_neg[4]:
    #         return colors_neg[3]
    #
    #     elif value < 0 and value <= percentiles_pos[0]:
    #         return 'white'
    #     elif value <= percentiles_pos[1]:
    #         return colors_pos[0]
    #     elif value <= percentiles_pos[2]:
    #         return colors_pos[1]
    #     elif value <= percentiles_pos[3]:
    #         return colors_pos[2]
    #     elif value <= percentiles_pos[4]:
    #         return colors_pos[3]
    #     else:
    #         return 'rgb(0,0,0)'
    #
    # df['color'] = df[col_value].apply(get_color)
    #
    #
    # # fig = px.density_mapbox(df, lat=col_y, lon=col_x, z=col_value, radius=10,
    # #                         center=dict(lat=y_med, lon=x_med), zoom=10,
    # #                         mapbox_style="open-street-map")
    #
    #
    # # fig = px.density_mapbox(df, lat=col_y, lon=col_x, z=col_value, radius=10,
    # #                         center=dict(lat=y_med, lon=x_med), zoom=9,
    # #                         mapbox_style="open-street-map")
    #
    # df['size']=0.1
    #
    # fig = px.scatter_mapbox(df, lat=col_y, lon=col_x, color='color', hover_name=col_value, hover_data={col_x: False, col_y: False, col_value: False, 'size':False, 'color':False}, size_max=1, size="size",
    #                            center=dict(lat=y_med, lon=x_med), zoom=11,
    #                          mapbox_style="open-street-map")
    #
    # # fig = px.scatter_mapbox(df, lat=col_y, lon=col_x,  hover_name=col_value, hover_data={col_x: False, col_y: False, col_value: False, 'size':False, 'color':False}, size_max=1, color_discrete_sequence=[df.color],  size="size",
    # #                            center=dict(lat=y_med, lon=x_med), zoom=9,
    # #                          mapbox_style="open-street-map")
    #
    fig.update_traces(
        marker=dict(sizemode='area', sizeref=2, sizemin=2)
        # Adjust sizeref and sizemin for smaller markers
    )

    # fig.update_traces(
    #     hovertemplate="<b>%{hovertext}</b><br>Value: %{marker.size}<extra></extra>"
    # )

    # print('WTF!!')

    coords_lat=df[col_y]

    coords_lon=df[col_x]

    coordinates = [[coords_lon.min(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.max()],
                   [coords_lon.min(), coords_lat.max()]]

    #fig.update_layout(mapbox_style='cartodbpositron', mapbox_layers = [{"coordinates": coordinates}])

    fig.update_layout(mapbox_layers=[{"coordinates": coordinates}],  autosize=True,
    margin=dict(l=0, r=0, t=0, b=0),
    height=1000)
    #fig.update_layout(mapbox_style='cartodbpositron')

    return fig

def plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct, unique_pi_module_name, diff_type):
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    df_PI_plans['BASELINE_VALUE']=1.0
    
    for y in list(range(start_year, end_year+1)):
        for p in list_plans:

            ### WORKAROUND so if value is missing it still continues....
            if len(df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==unique_PI_CFG.baseline_dct[Baseline])])>0:
                df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==unique_PI_CFG.baseline_dct[Baseline])].iloc[0].round(3)
            else:
                #print(f'WARNING value id missing for {p} during year {y}')
                df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = 0.000001
                
    df_PI_plans['DIFF_PROP']=((df_PI_plans[Variable]-df_PI_plans['BASELINE_VALUE'])/df_PI_plans['BASELINE_VALUE'])*100
    df_PI_plans['DIFF']=df_PI_plans[Variable]-df_PI_plans['BASELINE_VALUE']
    diff_dct={f'Values ({unit_dct[PI_code]})': 'DIFF', 'Proportion of reference value (%)': 'DIFF_PROP'}
    #diff_type= st.selectbox("Select a type of difference to compute", [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'])
    fig2=px.bar(df_PI_plans, x='YEAR', y=df_PI_plans[diff_dct[diff_type]], color='ALT', barmode='group', hover_data={'ALT': True, 'YEAR': True, diff_dct[diff_type]:True})
    fig2.update_layout(title=f'Difference between each selected plans and the reference for each year of the selected time period',
           xaxis_title='Years',
           yaxis_title=f'Difference in {diff_type}')
    
    return fig2

def plot_timeseries(df_PI, list_plans, Variable, plans_selected, Baseline, start_year, end_year, PI_code, unit_dct):
    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    fig = px.line(df_PI_plans, x="YEAR", y=Variable, color='ALT', labels={'ALT':'Plans'})
    fig['data'][-1]['line']['color']="#00ff00"
    fig['data'][-1]['line']['width']=3
    fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
           xaxis_title='Years',
           yaxis_title=f'{unit_dct[PI_code]}')
    return fig

def plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, unique_PI_CFG):
    multiplier = unique_PI_CFG.multiplier
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

def yearly_timeseries_data_prep(unique_pi_module_name, folder_raw, PI_code, plans_selected, Baseline, Region, start_year, end_year, Variable, CFG_DASHBOARD):
    
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_folder=os.path.join(folder_raw, PI_code, 'YEAR', 'SECTION')
    dfs=[]
    feather_done=[]
    plans_all=plans_selected+[Baseline]

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
    
    #unique_PI_CFG.dct_var.items()

    df_PI[Variable]=df_PI[f'{var}_{stats[0]}']

    multiplier=unique_PI_CFG.multiplier
    df_PI[Variable]=df_PI[Variable]*multiplier

    df_PI=df_PI[['YEAR', 'ALT', 'SECT', Variable]]
    
    return df_PI

def MAIN_FILTERS_streamlit(unique_pi_module_name, CFG_DASHBOARD, Years, Region, Plans, Baselines, Stats, Variable):
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
        #available_sections={i for i in CFG_DASHBOARD.sect_dct if all(item in unique_PI_CFG.available_sections for item in  CFG_DASHBOARD.sect_dct[i])}
        available_sections=list(unique_PI_CFG.sect_dct.keys())
        Regions=st.selectbox("Select regions", available_sections)
        
    else:
        Regions='N/A'
  
    if Plans:
        #available_plans={i for i in CFG_DASHBOARD.plan_dct if CFG_DASHBOARD.plan_dct[i] in unique_PI_CFG.available_plans}
        available_plans=list(unique_PI_CFG.plan_dct.keys())
        plans_selected=st.multiselect('Regulation plans to compare', available_plans, max_selections=CFG_DASHBOARD.maximum_plan_to_compare, default=next(iter(available_plans)))
    else:
        plans_selected='N/A'
        
    if Baselines:
        #baselines={i for i in CFG_DASHBOARD.baseline_dct if CFG_DASHBOARD.baseline_dct[i] in unique_PI_CFG.available_baselines}
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