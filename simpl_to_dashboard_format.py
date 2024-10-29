import pandas as pd
import os
import shutil


dash_res_folder=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS'

##Format Emile:

#PI_1D

format='DT'

plans=['1958DD', 'Bv7_2014', 'Bv7_GERBL1', 'PreProjectHistorical', 'OBS']

pi='IXEX_RPI_2D'

print(fr'processing...{pi}')

dim=pi.split('_')[-1]

if format=='EC' and dim=='1D':

    src=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\{pi}'

    liste=os.listdir(src)
    print(liste)

    for p in plans:

        for l in liste:

            if p not in l:
                continue
            else:
                path1 = os.path.join(src, l, p, 'sections')

                sections=os.listdir(path1)
                print(path1)

                for section in sections:

                    path2=os.path.join(path1, section, f'{pi}_{p}_{section}.feather')

                    print(path2)

                    df=pd.read_feather(path2)

                    print(df.head())

                    dst_plan=os.path.join(dash_res_folder, pi, p)

                    if not os.path.exists(dst_plan):
                        os.makedirs(dst_plan)

                    dst_section=os.path.join(dst_plan, section)

                    if not os.path.exists(dst_section):
                        os.makedirs(dst_section)

                    dst_finale=os.path.join(dst_section, f'{pi}_{p}_{section}.feather')

                    print(dst_finale)

                    shutil.copy2(path2, dst_finale)

if format=='DT' and dim=='2D':
    src = fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\{pi}'

    liste = os.listdir(src)
    print(liste)

    for p in plans:
        for l in liste:
            if p not in l:
                continue
            else:
                path1 = os.path.join(src, l, 'dashboard', p)
                if not os.path.exists(path1):
                    continue
                dst_pi=os.path.join(dash_res_folder, pi)
                if not os.path.exists(dst_pi):
                    os.makedirs(dst_pi)
                dst_plan = os.path.join(dst_pi, p)
                print(fr'copying {path1} to {dst_plan}....')
                shutil.move(path1, dst_plan)


quit()


#     path=os.path.join(src, l)
#     df=pd.read_csv(path, sep=';')
#     #print(df.head())
#
#     sect=l.split('_')[3:]
#     print(sect)
#     if len(sect)>1:
#         sect='_'.join(sect)
#     else:
#         sect=sect[0]
#
#     print(sect)
#     sect=sect.replace('.csv', '')
#     print(sect)
#
#     columns=['WINTER_YEAR', 'PLV_min_year']
#
#     df=df[columns]
#
#     dict_dash = {'WINTER_YEAR': 'YEAR', 'PLV_min_year': 'VAR1'}
#     df = df.rename(dict_dash, axis=1)
#
#     print(df.head())
#     path_dst = fr'{dst}\{sect}'
#
#     if not os.path.exists(path_dst):
#         os.makedirs(path_dst)
#
#     file_dst = f'{pi}_{plan}_{sect}.feather'
#     df.to_feather(fr'{path_dst}\{file_dst}')
# quit()