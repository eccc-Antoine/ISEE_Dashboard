import pandas as pd
import os

pi='ONZI_1D'

plan='PRE_PROJ'

src=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\{pi}\{pi}_S_{plan}'

dst=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS\{pi}\{plan}'

liste=os.listdir(src)


for l in liste:
    path=os.path.join(src, l)
    df=pd.read_csv(path, sep=';')
    #print(df.head())

    sect=l.split('_')[3:]
    print(sect)
    if len(sect)>1:
        sect='_'.join(sect)
    else:
        sect=sect[0]

    print(sect)
    sect=sect.replace('.csv', '')
    print(sect)



    columns=['WINTER_YEAR', 'PLV_min_year']

    df=df[columns]

    dict_dash = {'WINTER_YEAR': 'YEAR', 'PLV_min_year': 'VAR1'}
    df = df.rename(dict_dash, axis=1)

    print(df.head())
    path_dst = fr'{dst}\{sect}'

    if not os.path.exists(path_dst):
        os.makedirs(path_dst)

    file_dst = f'{pi}_{plan}_{sect}.feather'
    df.to_feather(fr'{path_dst}\{file_dst}')
quit()