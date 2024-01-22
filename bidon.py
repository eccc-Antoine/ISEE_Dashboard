import pandas as pd
import os

#===============================================================================
# df=pd.read_feather(r"M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\MUSK_1D\Baseline\USL_CAN\MUSK_1D_Baseline_USL_CAN.feather")
# 
# print(df.head())
# 
# quit()
#===============================================================================

folder=fr'M:\ISEE_Dashboard\ISEE_POST_PROCESS_DATA'

liste_files=[]
for root, dirs, files in os.walk(folder):
    for name in files:
        liste_files.append(os.path.join(root, name))
         
liste_done=[]
for file in liste_files:
    src=file
    print(src)
    dst=src.replace('.feather', '.csv')
    df=pd.read_feather(src)
    df.to_csv(dst, sep=';')
    os.remove(src)
    
quit()


#===============================================================================
# res_folder=r'M:\ISEE_Dashboard\ISEE_RAW_DATA\SAUV_2D'
# plans=['Alt_1', 'Alt_2', 'Baseline']
# sections=['USL_CAN', 'LKO_CAN']
# years=list(range(1926, 2017))
# for p in plans:
#     for s in sections:
#         for y in years:
#             folder=fr'{res_folder}\{p}\{s}\{y}'
#             liste_files=[]
#             for root, dirs, files in os.walk(folder):
#                 for name in files:
#                     liste_files.append(os.path.join(root, name))
#                      
#             liste_done=[]
#             for file in liste_files:
#                 src=file
#                 #print(src.split('\\')[-1])
#                 #print(src)
#                  
#                 tile=src.split('_')[-1].replace('.feather','')
#                 #print(tile)
#                 dst=src.replace(src.split('\\')[-1], f'SAUV_2D_{p}_{s}_{tile}_{y}.feather')
#                 #print(dst)
#                 #quit()
#                 if not src in liste_done:
#                     os.rename(src, dst)
#                     liste_done.append(src)
#                     liste_done.append(dst)
#                     print('renamed')
#                      
#                 else:
#                     print('not renamed')
# quit()
#===============================================================================
