import pandas as pd
import os

src=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\CHNI_2D'

liste_files=[]

for root, dirs, files in os.walk(src):
    for name in files:
        liste_files.append(os.path.join(root, name))

for l in liste_files:
    df=pd.read_feather(l)
    df['VAR1']=df['NBREED_PAIRS_CHNI']
    df=df[['PT_ID', 'XVAL', 'YVAL', 'VAR1']]

    df.to_feather(l)

quit()
