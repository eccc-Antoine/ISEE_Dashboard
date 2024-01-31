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

def prep_data_map_1d(file, start_year, end_year, stat, var, gdf_grille_origine, sct_map_dct, s, var_stat):
    if CFG_DASHBOARD.file_ext =='.feather':
        df=pd.read_feather(file)
    else:
        df=pd.read_csv(file, sep=';')
        
    df=df.loc[(df['YEAR']>=start_year) & (df['YEAR']<=end_year)]
    
    if stat=='Min':
        val=df[f'{var}_{var_stat}'].min()
    if stat=='Max':
        val=df[f'{var}_{var_stat}'].max()
    if stat=='mean':
        val=df[f'{var}_{var_stat}'].mean()
    if stat=='sum':
        val=df[f'{var}_{var_stat}'].sum()
         
    val=np.round(val, 3)
    
    gdf_grille=gdf_grille_origine

    gdf_grille['VAL'].loc[gdf_grille['SECTION'].isin(sct_map_dct[s])]=val
    
    #############
    
    '''cree une entite geo qui merge tout ca ensemble et lui donner la valeur de lune des sections plus delete ce qu'on vient de merger'''
    
    for g in list(sct_map_dct.values()):
        if len(g) >1:
            
            gdf_temp=gdf_grille.loc[gdf_grille['SECTION'].isin(g)]
            #print(gdf_temp)
            value=gdf_grille['VAL'].loc[gdf_grille['SECTION']==g[0]].iloc[0]
            gdf_temp=gdf_temp.dissolve()
            gdf_temp['VAL']=value
            #print([k for k, v in sct_map_dct.items() if v == g][0])
            gdf_temp['SECTION']=[k for k, v in sct_map_dct.items() if v == g][0]
            #print(gdf_temp)
            gdf_grille=pd.concat([gdf_grille, gdf_temp])

        else:
            pass
    
    
    gdf_grille=gdf_grille.loc[gdf_grille['SECTION'].isin(sct_map_dct.keys())]

        
    ##############

    return gdf_grille


def prep_for_prep_1d(sect_dct, sct_poly, folder, PI_code, scen_code, avail_years, stat, var, sct_map_dct, unique_pi_module_name):
    sections=[]
    for r in sect_dct.values():
        for rr in r:
            sections.append(rr)
    ## keep only unique values
    set_res = set(sections)         
    list_sect = (list(set_res))
    
    gdf_grille_origin=gpd.read_file(sct_poly)
    gdf_grille_origin['VAL']=0.0
    
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    var_stat=unique_PI_CFG.var_agg_stat[var][0]
    #sect_PI=unique_PI_CFG.available_sections
    gdfs=[]
    
    for s in list_sect:
        #if s in sect_PI:
        df_folder=os.path.join(folder, PI_code, 'YEAR', 'SECTION',  scen_code, s)
        pt_id_file=os.path.join(df_folder, f'{PI_code}_YEAR_{scen_code}_{s}_{np.min(avail_years)}_{np.max(avail_years)}{CFG_DASHBOARD.file_ext}')
        gdf_grille_unique=prep_data_map_1d(pt_id_file, np.min(avail_years), np.max(avail_years), stat, var, gdf_grille_origin, sct_map_dct, s, var_stat)
        gdfs.append(gdf_grille_unique)
        
    gdf_grille_all=pd.concat(gdfs)
    gdf_grille_all=gdf_grille_all.loc[gdf_grille_all['VAL']!=0]
    
    gdf_grille_all=gdf_grille_all.dissolve(by='SECTION', as_index=False)
    
    return gdf_grille_all

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

def popup_html(z, col, plan, stat, var, type):
    #sect_id=f'Section: {z["properties"]["SECTION"]}'
    #val=f'Value: {z["properties"][col]}'
    if type == 'diff':
        text=f'Difference of {stat} {var} in {z["properties"]["SECTION"]} under {plan} compared to Reference Plan is {z["properties"][col]}'
    else:
        text=f'{stat} of {var} in {z["properties"]["SECTION"]} under {plan} is {z["properties"][col]}'
    html = """
    <!DOCTYPE html>
    <html>
    <center><p> """ + text + """ </p></center>
    </html>
    """
    return html

def create_folium_map(gdf_grille, col, dim_x, dim_y, plan, stat, var, type):
    folium_map = folium.Map(location=[43.9, -76.3], zoom_start=7, tiles='cartodbpositron')
                    
    gdf_grille[col]=gdf_grille[col].astype(float)
    
    gjson = gdf_grille.to_crs(epsg='4326').to_json()

    js_data = json.loads(gjson)
    val_dict = gdf_grille.set_index("SECTION")[col]
    
    linear = cm.LinearColormap(["green", "yellow", "orange", "red"], vmin=gdf_grille[col].min(), vmax=gdf_grille[col].max())
    
    
    folium.GeoJson(
        gjson,
        style_function=lambda feature: {
            "fillColor": linear(val_dict[feature["properties"]["SECTION"]]),
            "color": "black",
            "weight": 2,
            "dashArray": "5, 5",
        },
    ).add_to(folium_map)
      
    for z in js_data['features']:
        b = folium.GeoJson(z['geometry'], style_function=lambda feature: {
            "color": "black",
            "weight": 2,
            "dashArray": "5, 5",})
            #tooltip=f'Section: {z["properties"]["SECTION"]} \n Value:{z["properties"][col]}', name='Sections')
        html = popup_html(z, col, plan, stat, var, type)
        b.add_child(folium.Popup(folium.Html(html, script=True), min_width=50, max_width=100))
        b.add_to(folium_map)
     
    folium_static(folium_map, dim_x, dim_y)

def folium_static(fig, width, height):
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)
        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width
            )
 
    elif isinstance(fig, plugins.DualMap):
        return components.html(
            fig._repr_html_(), height=height + 10, width=width
        )

def prep_data_map(file, start_year, end_year, id_col, col_x, col_y, stat, Variable):
    if CFG_DASHBOARD.file_ext =='.feather':
        df=pd.read_feather(file)
    else:
        df=pd.read_csv(file, sep=';')
    liste_year=list(range(start_year, end_year+1))
    liste_year = [str(i) for i in liste_year]
    columns=[id_col, col_x, col_y] + liste_year
    df=df[columns]
    if stat=='Min':
        df['stat']=df[liste_year].min(axis=1)
    if stat=='Max':
        df['stat']=df[liste_year].max(axis=1)
    if stat=='Mean':
        df['stat']=df[liste_year].mean(axis=1)
    if stat=='Sum':
        df['stat']=df[liste_year].sum(axis=1)
        
    df['stat']=df['stat'].round(3)
    df[Variable]=df['stat']
    df=df[[id_col, col_x, col_y, Variable]]
    df.dropna(subset=[Variable], inplace=True)
    return df

def plot_map(PIs, Variable, df, col_x, col_y, id_col, unique_pi_module_name, plan, col_value):  
    
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    fig = px.scatter_mapbox(df, lat=col_y, lon=col_x, hover_data={ id_col: False, col_x: False, col_y: False, col_value: f':{unique_PI_CFG.units}'},
            color=col_value, color_continuous_scale='ylorrd',  zoom=10, height=1000)
    coords_lat=df[col_y]
    coords_lon=df[col_x]
    coordinates = [[coords_lon.min(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.max()],
                   [coords_lon.min(), coords_lat.max()]]
    #fig.update_layout(mapbox_style="carto-darkmatter", mapbox_layers = [{"coordinates": coordinates}])
    fig.update_layout(mapbox_style="carto-positron", mapbox_layers = [{"coordinates": coordinates}])
    fig.update_layout(title=f'{Variable} in {unique_PI_CFG.units}',  title_font_size=20 )        
    return fig

def plot_map_plotly(PIs, Variable, df, col_x, col_y, id_col, unique_pi_module_name, plan, col_value):  
    
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    
    fig =  px.scatter_mapbox(df, lat=col_y, lon=col_x, hover_data={ id_col: False, col_x: False, col_y: False, col_value: f':{unique_PI_CFG.units}'},
        color=col_value, color_continuous_scale='ylorrd',  zoom=10, height=1000)
    
    
    coords_lat=df[col_y]
    coords_lon=df[col_x]
    coordinates = [[coords_lon.min(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.min()],
                   [coords_lon.max(), coords_lat.max()],
                   [coords_lon.min(), coords_lat.max()]]
    #fig.update_layout(mapbox_style="carto-darkmatter", mapbox_layers = [{"coordinates": coordinates}])
    fig.update_layout(mapbox_style="carto-positron", mapbox_layers = [{"coordinates": coordinates}])
    fig.update_layout(title=f'{Variable} in {unique_PI_CFG.units}',  title_font_size=20 )        
    return fig

def plot_difference_timeseries(df_PI, list_plans, Variable, Baseline, start_year, end_year, PI_code, unit_dct, unique_pi_module_name, diff_type):
    unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{unique_pi_module_name}')
    df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
    df_PI_plans['BASELINE_VALUE']=1
    
    for y in list(range(start_year, end_year+1)):
        for p in list_plans:

            ### WORKAROUND so if value is missing it still continues....
            if len(df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==unique_PI_CFG.baseline_dct[Baseline])])>0:
                df_PI_plans['BASELINE_VALUE'].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==p)] = df_PI_plans[Variable].loc[(df_PI_plans['YEAR']==y) & (df_PI_plans['ALT']==unique_PI_CFG.baseline_dct[Baseline])].iloc[0]
            else:
                print(f'WARNING value id missing for {p} during year {y}')
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
    fig['data'][0]['line']['color']="#00ff00"
    fig['data'][0]['line']['width']=3
    fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
           xaxis_title='Years',
           yaxis_title=f'{unit_dct[PI_code]}')
    return fig

def plan_aggregated_values(Stats, plans_selected, Baseline, Variable, df_PI, unique_PI_CFG):
    if Stats == 'mean':
        plan_values=[]
        baseline_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.baseline_dct[Baseline]].mean().round(3)
        for c in range(len(plans_selected)):
            plan_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.plan_dct[plans_selected[c]]].mean().round(3)
            plan_values.append(plan_value)

    if Stats == 'sum':
        plan_values=[]
        baseline_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.baseline_dct[Baseline]].sum().round(3)
        for c in range(len(plans_selected)):
            plan_value=df_PI[Variable].loc[df_PI['ALT']==unique_PI_CFG.plan_dct[plans_selected[c]]].sum().round(3)
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
    
    df_PI['SECT']=Region
    #unique_PI_CFG.dct_var.items()

    df_PI[Variable]=df_PI[f'{var}_{stats[0]}']

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