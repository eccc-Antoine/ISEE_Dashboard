import pandas as pd
import os

src=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS\NFB_2D'

dst=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS\NFB_2D_ASSET_num'

liste_files=[]

for root, dirs, files in os.walk(src):
    for name in files:
        liste_files.append(os.path.join(root, name))

print(len(liste_files))

for l in liste_files:

    print(l)
    if 'readme' in l:
        continue

    df=pd.read_feather(l)

    print(df['CLASS'].unique())
    quit()

    #df=df.loc[(df['CLASS']=='RES_PRIM')|(df['CLASS']=='RES_SEC')]

    df = df.loc[df['CLASS'] == 'ASSET']


    df=df.loc[(df['VAR1']!=0)|(df['VAR2']!=0)]

    df = df.drop(['VAR2'], axis=1)

    df['VALUE']=df['VAR1']

    df=df.drop(['VAR1'], axis=1)

    #var_dct={'VAR1':'OW', 'VAR2':'SAV', 'VAR3':'EM', 'VAR4':'WM', 'VAR5':'SW', 'VAR6':'UPL'}

    var_dct = {'VAR1': 'RES_PRIM', 'VAR2': 'RES_SEC'}

    for k in var_dct.keys():
        df[k]=0.0
        df.loc[df['CLASS']==var_dct[k], k]=df.loc[df['CLASS']==var_dct[k], 'VALUE']

    df['VAR3']=df['VAR2']+df['VAR1']
    #f.loc[df['class'].isin(['RES_PRIM', 'RES_SEC']), 'VAR3']=df.loc[['class']==var_dct[k], 'VALUE']
    df=df.drop(['CLASS'], axis=1)

    dst2=l.replace(src, dst)
    file_name=l.split('\\')[-1]
    dossier=dst2.replace(f'\\{file_name}', '')

    df = df.drop(['VALUE'], axis=1)

    rename_dct={'PT_ID':'PT_ID', 'TILE_ID':'TILE', 'SECT_CNTRY':'SECTION', 'LON':'LON', 'LAT':'LAT', 'VAR1':'VAR1', 'VAR2':'VAR2', 'VAR3':'VAR3'}

    df = df.rename(columns=rename_dct)

    if not os.path.exists(dossier):
        os.makedirs(dossier)

    df.to_feather(dst2)

quit()

