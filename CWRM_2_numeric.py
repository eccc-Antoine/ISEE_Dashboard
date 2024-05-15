import pandas as pd
import os

src=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\CWRM_2D'

dst=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\CWRM_2D_num'

liste_files=[]

for root, dirs, files in os.walk(src):
    for name in files:
        liste_files.append(os.path.join(root, name))

for l in liste_files:

    df=pd.read_feather(l)

    df['class']=df['VAR1']

    df=df.drop(['VAR1'], axis=1)

    var_dct={'VAR1':'OW', 'VAR2':'SAV', 'VAR3':'EM', 'VAR4':'WM', 'VAR5':'SW', 'VAR6':'UPL'}

    for k in var_dct.keys():
        df[k]=0.0
        df.loc[df['class']==var_dct[k], k]=0.01

    df['VAR7']=0.0
    df.loc[df['class'].isin(['SAV', 'EM', 'WM', 'SW', 'UPL']), 'VAR7']=0.01
    df=df.drop(['class'], axis=1)

    dst2=l.replace(src, dst)
    file_name=l.split('\\')[-1]
    dossier=dst2.replace(f'\\{file_name}', '')

    if not os.path.exists(dossier):
        os.makedirs(dossier)

    df.to_feather(dst2)

quit()

