import pandas as pd
import os
#===============================================================================
# "M:\DATA\ISEE\ISEE_POST_PROCESS_DATA\NAVC_1D\YEAR\SECTION\Bv7_infop_policy_620_nosepRule\USL\NAVC_1D_YEAR_Bv7_infop_policy_620_nosepRule_USL_1961_2020.feather"
# "M:\DATA\ISEE\ISEE_POST_PROCESS_DATA\NAVC_1D\YEAR\SECTION\Bv7_infop_policy_620_nosepRule\USL\NAVC_1D_YEAR_Bv7_infop_policy_620_nosepRule_USL_1961_2016.feather"
#===============================================================================


file=r"M:\DATA\ISEE\ISEE_RAW_DATA\ONZI_1D\Bv7baseline_v20240115\LKO\1D_ONZI_Bv7baseline_v20240115_LKO.feather"
df=pd.read_feather(file)
 
print(df.head())
 
print(df.tail())

print(list(df))

print(len(df))

quit()
#===============================================================================
# print(df['SECTION'].unique())
# 
# for s in df['SECTION'].unique():
#     df_s=df.loc[df['SECTION']==s]
#     print(s)
#     print(df_s['TILE'].unique())
#  
# #df.to_feather(r"M:\DATA\ISEE\ISEE_RAW_DATA\MM_2D\Bv7baseline_v20240115\LKO\MM_2D_Bv7baseline_v20240115_LKO.feather")
#  
# quit()
#===============================================================================



folder=fr"M:\DATA\ISEE\ISEE_RAW_DATA\ONZI_1D"

liste_files=[]
for root, dirs, files in os.walk(folder):

    for name in files:
        if '.csv' in name:
            os.remove(os.path.join(root, name))
        else:
            pass

quit()




#===============================================================================
# for f in liste_files:
#     
#     print(f)
#     
#     nom=f.split('\\')[-1]
#     
#     name=nom.split('_')
#     
#     plan=name[0]+'_'+name[1]
#     
#     section=name[2]
#     
#     PI=name[3]+'_1D'
#     
#     ext=name[-1]
# 
# 
#     new_name='ONZI_1D'+'_'+plan+'_'+section+ext
#         
#     print(new_name)
#     
#     #===========================================================================
#     # quit()
#     # 
#     # dst=name.replace('ONZI', 'ONZI_1D')
#     #===========================================================================
#     
#     desti=f.replace(nom, new_name)
#     
#     print(desti)
#     
#     
#     os.rename(f, desti)    
#     #===========================================================================
#     # 
#     # 
#     # 
#     # df=pd.read_csv(f, sep=';')
#     # df['YEAR']=df['WINTER_YEAR']
#     # df['VAR1']=df['PLV_min_year']
#     # df=df[['YEAR', 'VAR1']]
#     # name=f.split('\\')[-1]
#     # dst=name.replace('ONZI', 'ONZI_1D')
#     # dst=dst.replace('RESULTS_BY_YEAR.csv', '.feather')
#     # section=f.split('\\')[6]
#     # #name=f.split('\\')[-1]
#     # bad=name.split('_')[2]
#     # dst=dst.replace(bad, section)
#     # df.to_feather(dst)
#     # #os.remove(f)
#     #===========================================================================
# 
# quit()
#     
#         
# 
# 
# 
# df=pd.read_feather(r"M:\DATA\ISEE\ISEE_POST_PROCESS_DATA\NAVC_1D\YEAR\PLAN\Bv7_baseline_NG_historical\NAVC_1D_YEAR_Bv7_baseline_NG_historical_1961_2016.feather")
#  
# print(df.head())
# 
# print(df.dtypes)
# 
# quit()
# 
# df['VAR1']=df['VAR1']/2
# 
# df['VAR2']=df['VAR2']/2
# 
# print(df.head())
# 
# 
# 
# df.to_feather(r"M:\DATA\ISEE\ISEE_RAW_DATA\EX_RB_1D\Alt_2\USL_DS\EX_RB_1D_Baseline_USL_DS.feather")
#  
# quit()
# 
# 
# 
# folder=fr'M:\ISEE_Dashboard\ISEE_POST_PROCESS_DATA'
# 
# liste_files=[]
# for root, dirs, files in os.walk(folder):
#     for name in files:
#         liste_files.append(os.path.join(root, name))
#          
# liste_done=[]
# for file in liste_files:
#     src=file
#     print(src)
#     dst=src.replace('.feather', '.csv')
#     df=pd.read_feather(src)
#     df.to_csv(dst, sep=';')
#     os.remove(src)
#     
# quit()
#===============================================================================


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
