import pandas as pd
import os
import geopandas as gpd
#===============================================================================
# "M:\DATA\ISEE\ISEE_POST_PROCESS_DATA\NAVC_1D\YEAR\SECTION\Bv7_infop_policy_620_nosepRule\USL\NAVC_1D_YEAR_Bv7_infop_policy_620_nosepRule_USL_1961_2020.feather"
# "M:\DATA\ISEE\ISEE_POST_PROCESS_DATA\NAVC_1D\YEAR\SECTION\Bv7_infop_policy_620_nosepRule\USL\NAVC_1D_YEAR_Bv7_infop_policy_620_nosepRule_USL_1961_2016.feather"
#===============================================================================

import pandas as pd
import os

# gdf=gpd.read_file("H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\debug\section_tiles_countries.geojson")
#
# sections=gdf['SECTION'].unique()
#
# for s in sections:
#     gdf_s=gdf.loc[gdf['SECTION']==s]
#     tiles=gdf_s['tile'].unique()
#     print(s, list(tiles))
# quit()



df=pd.read_feather(r"P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\NFB_2D\YEAR\PT_ID\Bv7_2014_ComboC\USL_DS_CAN\VAR1_NFB_2D_YEAR_Bv7_2014_ComboC_USL_DS_CAN_PT_ID_178_1962_2020")


print(list(df))

#print(df['SECTION'].unique())

#df.to_csv(fr"T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW\ZIPA_1D\PreProjectHistorical\USL_DS\ZIPA_1D_PreProjectHistorical_USL_US.csv", sep=';', index=None)

#print(df['SECTION'].unique())
print(df.head())
#print(df)
quit()
#
# # tiles_2_merge=[238,237,226]
# #
# # src1=fr'\\131.235.232.206\prod2\GLAM\Input_ISEE\prod\GRID\grd_v42_20240320\Filtered_fea\LKO'
# # src2=fr'\\131.235.232.206\prod2\GLAM\Input_ISEE\prod\GRID\grd_v42_20240320\Filtered_fea\USL_US'
# # dst=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\Tiles'
# #
# # for t in tiles_2_merge:
# #     df1=pd.read_feather(fr'{src1}\GLAM_DEM_ISEE_TILE_{t}.feather')
# #     df2=pd.read_feather(fr'{src2}\GLAM_DEM_ISEE_TILE_{t}.feather')
# #     df3=pd.concat([df1, df2])
# #     print(len(df3), len(df2), len(df1))
# #     df3.to_feather(fr'{dst}\GLAM_DEM_ISEE_TILE_{t}.feather')
# # quit()
# #
# #
src=r'P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\IERM_2D'
liste_files=[]
for root, dirs, files in os.walk(src):
    for name in files:
        liste_files.append(os.path.join(root, name))

print(len(liste_files))
print(liste_files[0])
for l in liste_files:
    dst=l.replace('_1962_', '_1963_')
    if not os.path.exists(dst):
        os.rename(l, dst)
    else:
        os.remove(l)
    #
    #
    # df=pd.read_feather(l)
    # print(df.head())
    # print(df.tail())
    # #geometry = gpd.points_from_xy(df['LON'], df['LAT'])
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['LON'], df['LAT']), crs=32618)
    # gdf=gdf.to_crs(4326)
    # gdf['LON']=gdf.geometry.x
    # gdf['LAT'] = gdf.geometry.y
    # df=gdf.drop(columns=['geometry'])
    # print(df.head())
    # df.to_feather(l)
quit()




#
# for f in liste_files:
#     print(f)
#     df=pd.read_feather(f)
#     df['VAR1']=df['NBREED_PAIRS_CHNI']
#     df=df[['PT_ID', 'XVAL', 'YVAL', 'VAR1']]
#     df.to_feather(f)
# quit()


# src=fr'H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\CWRM_2D_num\Bv7\LKO'
#
# liste1=os.listdir(src)
#
# liste_tiles=[]
#
# for l in liste1:
#     # print(l)
#     path=os.path.join(src, l)
#     liste2=os.listdir(path)
#     # print(liste2)
#
#     for ll in liste2:
#         # print(ll.split('_')[-2])
#         tile=int(ll.split('_')[-2])
#         # tile=tile.replace("'", '')
#         if tile not in liste_tiles:
#             liste_tiles.append(tile)
# print(liste_tiles)
#
# quit()




# liste_files=[]
#
# for root, dirs, files in os.walk(src):
#     for name in files:
#         liste_files.append(os.path.join(root, name))
#
# for l in liste_files:
#     dst = l.replace('1D_ZIPA', 'ZIPA_1D')
#     os.rename(l, dst)
#
# quit()





#file=r""
#file=r"H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\CHNI_2D\Bv7_2014\SLR_US\1980\CHNI_2D_Bv7_2014_SLR_US_126_1980.feather"
file=r"H:\Projets\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\Tiles\GLAM_DEM_ISEE_TILE_78.feather"

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
