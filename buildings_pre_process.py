import os 

import pandas as pd

#===============================================================================
# folder=r'M:\DATA\ISEE\ISEE_RAW_DATA\BUILD_2D\BV7_P6\ON'
# 
# liste=os.listdir(folder)
# 
# for f in liste:
#     path=os.path.join(folder, f)
#     name=f.replace('_P7', '_P6')
#     dst=os.path.join(folder, name)
#     os.rename(path, dst)
# 
# quit()
#===============================================================================




folder=fr"M:\DATA\ISEE"

PI='BUILD_2D'
plans=['BV7_Baseline', 'BV7_P6']

plan_dct_1={'BV7_Baseline': 'BV7_Base', 'BV7_P6':'BV7_P6_Base'}

plan_dct_2={'BV7_Baseline':'Bv7baseline_v20240115', 'BV7_P6':'Bv7p620nosepinfop_v20240115'}

#reg=['ON', 'QC', 'US']

reg=['ON']

years=list(range(1980, 2020))

for p in plans:
    for y in years:
        dfs=[]
        for r in reg:
            df=pd.read_csv(fr'{folder}\{p}\{r}\{r}_{plan_dct_1[p]}_{y}.csv')
            if 'Fl50_Run' in list(df):
                df=df[['id_build', 'LON', 'LAT', 'Section', 'Fl50_Run', 'tile_id']]
                df.rename(columns={'id_build':'PT_ID', 'LON':'LON', 'LAT':'LAT', 'Section':'SECTION', 'Fl50_Run':'VAR1', 'tile_id':'TILE'}, inplace=True)
                #df['TILE']=df['TILE'].split(',')[0]
                df['TILE']=[x.split(',')[0] for x in df['TILE']]
                df['TILE']=df['TILE'].astype(int)
            else:
                df=df[['id_build', 'LON', 'LAT', 'Section', 'FL_Z50', 'tile_id']]
                df.rename(columns={'id_build':'PT_ID', 'LON':'LON', 'LAT':'LAT', 'Section':'SECTION', 'FL_Z50':'VAR1', 'tile_id':'TILE'}, inplace=True)
                #df['TILE']=df['TILE'].split(',')[0]
                df['TILE']=[x.split(',')[0] for x in df['TILE']]
                df['TILE']=df['TILE'].astype(int)
            #print(df['TILE'].unique())
            df=df.drop_duplicates(subset=['PT_ID'])
            print(r, len(df))
            print(df['SECTION'].unique())
            dfs.append(df)

        df_year=pd.concat(dfs)  
        
        print(len(df_year))
         
        dossier=fr'M:\DATA\ISEE\ISEE_RAW_DATA\{PI}\{plan_dct_2[p]}'
     
        if not os.path.exists(dossier):
            os.makedirs(dossier)
         
         
        df_year=df_year.drop_duplicates(subset=['PT_ID'])
        
        print(len(df_year))
         
        df_year=df_year.reset_index()
        
        print(len(df_year))
         
        df_year.to_feather(os.path.join(dossier, fr'{PI}_{plan_dct_2[p]}_{y}.feather'))  
        
quit()
        

#===============================================================================
# liste_files=[]
# for root, dirs, files in os.walk(folder):
# 
#     for name in files:
#         path=os.path.join(root, name)
#         liste_files.append(path)
# 
# count=0
# 
# for f in liste_files:
#     PI=f.split('\\')[4]
#     Plan=f.split('\\')[5]
#     plan_dct={'BV7_Baseline':'Bv7baseline_v20240115', 'BV7_P6':'Bv7p620nosepinfop_v20240115'}
#     Year=f.split('_')[-1].replace('.csv', '')
#     print(PI, Plan, Year)
#     count+=1
#     df=pd.read_csv(f)
#     if 'Fl50_Run' in list(df):
#         df=df[['id_build', 'LON', 'LAT', 'Section', 'Fl50_Run']]
#         df.rename(columns={'id_build':'PT_ID', 'LON':'LON', 'LAT':'LAT', 'Section':'SECTION', 'Fl50_Run':'VAR1'}, inplace=True)
#     else:
#         df=df[['id_build', 'LON', 'LAT', 'Section', 'FL_Z50']]
#         df.rename(columns={'id_build':'PT_ID', 'LON':'LON', 'LAT':'LAT', 'Section':'SECTION', 'FL_Z50':'VAR1'}, inplace=True)
# 
#     dossier=fr'M:\DATA\ISEE\ISEE_RAW_DATA\{PI}\{plan_dct[Plan]}'
#     
#     if not os.path.exists(dossier):
#         os.makedirs(dossier)
#     
#     df.to_feather(os.path.join(dossier, fr'{PI}_{plan_dct[Plan]}_{Year}.feather'))
#     
#         
#===============================================================================
quit()
