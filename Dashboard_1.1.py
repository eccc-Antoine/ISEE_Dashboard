import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
import os
import plotly.figure_factory as ff

folder='F:\Dash\dash_app_example\static\Streamlit_test'
liste=os.listdir(folder)
pis_code=[]
for f in liste:
    code=f.split('_')[0]
    pis_code.append(code)

pi_dct={'PRSD': 'Building Damages', 'WET': 'Wetland area'}

unit_dct={'PRSD': 'M$', 'WET': 'ha'}

pis=[]

for pi in pis_code:
    pi_name=pi_dct[pi]
    pis.append(pi_name)

sect_dct={'Haut-Richelieu':[20], 'Bas-Richelieu':[12], 'Canada':[12, 20] }
countries=list(sect_dct.keys())



baselines=['actual plan', 'pristine state']
baseline_dct={'actual plan': 'Baseline', 'pristine state': 'Baseline'}
plans=[]
for i in range(1,4):
    plan=f'Plan {str(i)}'
    plans.append(plan)
    
plan_dct={'Plan 1': 'Alt_1', 'Plan 2': 'Alt_2', 'Plan 3': 'Alt_3'}

# read csv from a github repo
#df = pd.read_csv("https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv")


st.set_page_config(
    page_title = 'ISEE Dashboard',
    page_icon = ':floppy_disk:',
    layout = 'wide'
)

# dashboard title

st.title("ISEE Dashboard")


Col1, Col2 = st.columns([0.2, 0.8])

with Col1:
# top-level filters 
    PIs= st.selectbox("Select Performance indicator to display", pis)
    
    start_year, end_year=st.select_slider('Select a period', options=list(range(1925, 2018)), value=(2000, 2005))
    #st.write(fr'Results will be processed for {start_year} to {end_year} period')
    
    Region=st.selectbox("Select regions", countries)
    #st.write(fr'Results will be processed for {start_year} to {end_year} period')
    
    plans_selected=st.multiselect('Regulation plans to compare', plans, max_selections=3, default=plans[0:3])
    
    Baseline=st.selectbox("Select a reference plan", baselines)
    
    Stats=st.selectbox("Stats to compute", ['average', 'sum'])
    
    #job_filter = st.selectbox("Ignore this for now :)", pd.unique(df['job']))
    
    #st.subheader(f'Now showing :blue[{Stats}] of :blue[{PIs}], during :blue[{start_year} to {end_year}] period, in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')
    #st.write(f'Now showing results for {PIs}, during {start_year} to {end_year} period, in {Region} \n\r Where {plans_selected} are compared to {job_filter}')

with Col2: 
    placeholder1 = st.empty()
    with placeholder1.container():
        st.subheader(f'Now showing :blue[{Stats}] of :blue[{PIs}], during :blue[{start_year} to {end_year}] period, in :blue[{Region}] where :blue[{plans_selected}] are compared to :blue[{Baseline}]')

    placeholder2 = st.empty()
    
    ##old stuff
    #df = df[df['job']==job_filter]

    ##new_stuff
    key_list = list(pi_dct.keys())
    val_list = list(pi_dct.values())
    position = val_list.index(PIs)
    PI_code=key_list[position]
    df_PI=pd.read_csv(fr'{folder}\{PI_code}_alts.csv', sep=';')
    ##filters
    #year
    df_PI=df_PI.loc[(df_PI['YEAR']>=start_year) & (df_PI['YEAR']<=end_year)]
    #region
    df_PI=df_PI.loc[df_PI['SECT_ID'].isin(sect_dct[Region])]
    
    #merge by year if more than one region selected 
    #if len(df_PI['SECT_ID'].unique())>1:
    df_PI=df_PI[['YEAR', 'VALUE', 'ALT']]
    df_PI=df_PI.groupby(by=['YEAR', 'ALT'], as_index=False).sum()
        

    if Stats == 'average':
        baseline_value=df_PI['VALUE'].loc[df_PI['ALT']==baseline_dct[Baseline]].mean().round(3)
        if len(plans_selected)>0:
            plan1_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[0]]].mean().round(3)
        if len(plans_selected)>1:
            plan2_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[1]]].mean().round(3)
        if len(plans_selected)>2:
            plan3_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[2]]].mean().round(3)
        
    if Stats == 'sum':
        baseline_value=df_PI['VALUE'].loc[df_PI['ALT']==baseline_dct[Baseline]].sum().round(3)
        if len(plans_selected)>0:
            plan1_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[0]]].sum().round(3)
        if len(plans_selected)>1:
            plan2_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[1]]].sum().round(3)
        if len(plans_selected)>2:
            plan3_value=df_PI['VALUE'].loc[df_PI['ALT']==plan_dct[plans_selected[2]]].sum().round(3)

    with placeholder2.container():
    # create three columns
        kpi1, kpi2, kpi3 = st.columns(3)
        
        if len(plans_selected)==0:
            st.write('You must at least select one regulation plan to compare')
        
        if len(plans_selected)>0:
        #kpi1.metric(label="Age", value=round(avg_age), delta= round(avg_age) - 10)
            kpi1.metric(label=fr'{plans_selected[0]} {Stats} ({unit_dct[PI_code]})', value=round(plan1_value), delta= round(plan1_value) -round(baseline_value))
        
        if len(plans_selected)>1:
        #kpi2.metric(label="Married Count 💍", value= int(count_married), delta= - 10 + count_married)
            kpi2.metric(label=fr'{plans_selected[1]} {Stats} ({unit_dct[PI_code]})', value=round(plan2_value), delta= round(plan2_value) -round(baseline_value))
        
        if len(plans_selected)>2:
        #kpi3.metric(label="A/C Balance ＄", value= f"$ {round(balance,2)} ", delta= - round(balance/count_married) * 100)
            kpi3.metric(label=fr'{plans_selected[2]} {Stats} ({unit_dct[PI_code]})', value=round(plan3_value), delta= round(plan3_value) -round(baseline_value))
    
    placeholder3 = st.empty()
    with placeholder3.container():
        tab1, tab2, tab3, tab4 = st.tabs(["Timeseries", "Difference", "Maps", "Data"])
        list_plans=[]
        for p in plans_selected:
            pp=plan_dct[p]
            list_plans.append(pp)
        #list_plans= plan_dct[plans_selected]
        list_plans.append(baseline_dct[Baseline])
        
        with tab1:
            df_PI_plans= df_PI.loc[df_PI['ALT'].isin(list_plans)]
            fig = px.line(df_PI_plans, x="YEAR", y="VALUE", color='ALT')
            fig.update_layout(title=f'Values of {plans_selected} compared to {Baseline} from {start_year} to {end_year}',
                   xaxis_title='Years',
                   yaxis_title=f'{unit_dct[PI_code]}')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:  
            df_PI['BASELINE_VALUE']=1

            for y in list(range(start_year, end_year+1)):
                for p in list_plans:
                    df_PI['BASELINE_VALUE'].loc[(df_PI['YEAR']==y) & (df_PI['ALT']==p)] = df_PI['VALUE'].loc[(df_PI['YEAR']==y) & (df_PI['ALT']==baseline_dct[Baseline])].iloc[0]

            df_PI['DIFF_PROP']=((df_PI['VALUE']-df_PI['BASELINE_VALUE'])/df_PI['BASELINE_VALUE'])*100
            df_PI['DIFF']=df_PI['VALUE']-df_PI['BASELINE_VALUE']
            diff_dct={f'Values ({unit_dct[PI_code]})': 'DIFF', 'Proportion of reference value (%)': 'DIFF_PROP'}
            diff_type= st.selectbox("Select a type of difference to compute", [f'Values ({unit_dct[PI_code]})', 'Proportion of reference value (%)'])
            fig2=px.bar(df_PI, x='YEAR', y=df_PI[diff_dct[diff_type]], color='ALT', barmode='group', hover_data={'ALT': True, 'YEAR': False, diff_dct[diff_type]:True})
            fig2.update_layout(title=f'Difference between each selected plans and the reference for each year of the selected time period',
                   xaxis_title='Years',
                   yaxis_title=f'Difference in {diff_type}')
            st.plotly_chart(fig2, use_container_width=True)
            

        with tab3:
            
            #### HRADCODED ### need to tranfer all the data in order to work!!
            precise_folder=fr'F:\LCRR_Antoine\PI_ENV\ISEE_2\LCRR\results_clean\ESLU_2D'
            
            #st.write('Please wait this is a lot of data to process :sweat_smile:')
            
            ze_plan=st.selectbox("Select a plan to display on map", plans_selected)
            
            ze_plan=plan_dct[ze_plan]
            
            #for p in list_plans:
            alt=fr'{precise_folder}\{ze_plan}'
            dfs_s=[]
            for s in sect_dct[Region]:
                reg=fr'{alt}\Section_{s}'
                tiles=os.listdir(reg)
                dfs_t=[]
                for t in tiles:
                    print(tiles)
                    dfs_y=[]
                    tile=fr'{reg}\{t}'
                    for y in list(range(start_year, end_year+1)):
                        ### HARDCODED ###
                        df_y=pd.read_csv(fr'{tile}\ESLU_2D_CAN_{y}_Section_{s}_{t}.csv', sep=';')
                        df_y=df_y[['PT_ID', 'XVAL', 'YVAL', 'HSI']]
                        dfs_y.append(df_y)
                    df_t=pd.concat(dfs_y, ignore_index=True)
                    dfs_t.append(df_t)
                df_s=pd.concat(dfs_t, ignore_index=True)
                dfs_s.append(df_s)
            df_p=pd.concat(dfs_s, ignore_index=True)
            if Stats == 'sum':
                df_p=df_p.groupby(by=['PT_ID', 'XVAL', 'YVAL'], as_index=False).sum()
            if Stats == 'average':
                df_p=df_p.groupby(by=['PT_ID', 'XVAL', 'YVAL'], as_index=False).mean()
            print(df_p.head())
            #st.write('done!')
            print(len(df_p))
            print(len(df_p['PT_ID'].unique()))         
                            
            
            
            
            
    #===========================================================================
    #         df_PI_precise=pd.read_csv(fr'{folder}\{PI_code}_precise.csv', sep=';')
    #             ##filters
    #         #year
    #         df_PI_precise=df_PI_precise.loc[(df_PI_precise['YEAR']>=start_year) & (df_PI_precise['YEAR']<=end_year)]
    #         
    #         #region
    #         df_PI_precise=df_PI_precise.loc[df_PI_precise['SECT_ID'].isin(sect_dct[Region])]
    #         
    #         #merge by year if more than one region selected >1:
    #         df_PI_precise=df_PI_precise[['YEAR', 'VALUE', 'ALT']]
    #         df_PI_precise=df_PI_precise.groupby(by=['YEAR', 'ALT'], as_index=False).sum()
    # 
    #         'put some maps here'
    #===========================================================================
            
        with tab4:
            #'put some Data here'
            df_PI['YEAR']=df_PI['YEAR'].astype(str)
            st.dataframe(df_PI.style, hide_index=True)
    

#===============================================================================
# # creating a single-element container.
# placeholder = st.empty()
# 
# # dataframe filter 
# 
# df = df[df['job']==job_filter]
# 
# #pi_code={i for i in pi_dct if pi_dct[i]==PIs}
# key_list = list(pi_dct.keys())
# val_list = list(pi_dct.values())
# position = val_list.index(PIs)
# PI_code=key_list[position]
# 
# #rint(pi_code)
# 
# df_PI=pd.read_csv(fr'{folder}\{PI_code}_alts.csv', sep=';')
# 
# # near real-time / live feed simulation 
# 
# #for seconds in range(200):
# #while True: 
#     
# df['age_new'] = df['age'] * np.random.choice(range(1,5))
# df['balance_new'] = df['balance'] * np.random.choice(range(1,5))
# 
# # creating KPIs 
# avg_age = np.mean(df['age_new']) 
# 
# count_married = int(df[(df["marital"]=='married')]['marital'].count() + np.random.choice(range(1,30)))
# 
# balance = np.mean(df['balance_new'])
# 
# with placeholder.container():
#     # create three columns
#     kpi1, kpi2, kpi3 = st.columns(3)
# 
#     # fill in those three columns with respective metrics or KPIs 
#     kpi1.metric(label="Age", value=round(avg_age), delta= round(avg_age) - 10)
#     kpi2.metric(label="Married Count 💍", value= int(count_married), delta= - 10 + count_married)
#     kpi3.metric(label="A/C Balance ＄", value= f"$ {round(balance,2)} ", delta= - round(balance/count_married) * 100)
# 
#     # create two columns for charts 
# 
#     fig_col1, fig_col2 = st.columns(2)
#     with fig_col1:
#         st.markdown("### First Chart")
#         fig = px.density_heatmap(data_frame=df, y = 'age_new', x = 'marital')
#         st.write(fig)
#     with fig_col2:
#         st.markdown("### Second Chart")
#         fig2 = px.histogram(data_frame = df, x = 'age_new')
#         st.write(fig2)
#     st.markdown("### Detailed Data View")
#     st.dataframe(df)
#===============================================================================
        #time.sleep(1)
    #placeholder.empty()