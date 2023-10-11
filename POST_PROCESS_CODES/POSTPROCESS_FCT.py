import os
import pandas as pd
import geopandas as gpd
import shutil
import importlib
import CFG_POST_PROCESS as cfg



class POST_PROCESS_2D:
    
    def __init__(self, pis, plans, sections, years, ISEE_RES, POST_PROCESS_RES, sep, dct_sect):

        self.pis=pis
        self.plans=plans
        self.sections=sections
        self.years=years
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        self.dct_sect=dct_sect
           
    def agg_YEAR(self, folder_space, y):  

        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        df_year=pd.DataFrame()
        liste_df=[]
        liste_file_year=[f for f in liste_files if str(y) in f]
        for csv in liste_file_year:
            df_temp=pd.read_csv(csv, sep=self.sep)
            liste_df.append(df_temp)
        df_year=pd.concat(liste_df, ignore_index=True)
        return df_year
    
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_csv_year):
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        df_space[AGG_TIME]=self.years
        if not os.path.exists(path_res):
            os.makedirs(path_res)
        for y in self.years:
            if AGG_SPACE == 'PLAN' or AGG_SPACE == 'SECTION':               
                df_year=self.agg_YEAR(agg_year_param, y)
            if AGG_SPACE == 'TILE':
                path_csv_year2=path_csv_year.replace('foo', str(y))
                df_year=pd.read_csv(path_csv_year2, sep=self.sep)
            for var in list_var:
                for stat in stats:
                    if stat=='sum':
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].sum()
                    elif stat=='mean':
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].mean()
                    else:
                        print('STAT value provided is unavailable')   
        df_space.to_csv(os.path.join(path_res, res_name), sep=self.sep, index=False)

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE, stats):
        
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata 
        AGG_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM']
        AGG_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION', 'TILE', 'PT_ID']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean'] 
        '''
        for AGG_TIME in AGGS_TIME:
            for AGG_SPACE in AGGS_SPACE:  
                
                pi_module_name=f'CFG_{PI}'
                PI_CFG=importlib.import_module( pi_module_name)
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)
                        
                if AGG_TIME=='YEAR':
                    if AGG_SPACE=='PLAN':
                        for space in self.plans:
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(self.years)}_{max(self.years)}.csv'
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'')
                              
                    elif AGG_SPACE=='SECTION':
                        for p in self.plans:
                            for space in self.sections:
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(self.years)}_{max(self.years)}.csv'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p, space)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '')

                    elif AGG_SPACE=='TILE':
                        for p in self.plans:
                            for s in self.sections: 
                                for space in self.dct_sect[s]:
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(self.years)}_{max(self.years)}.csv'
                                    path_csv_year=os.path.join(self.ISEE_RES, PI, p, s, 'foo' , f'{PI}_foo_{s}_{space}.csv')
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, '', path_csv_year)

                    elif AGG_SPACE=='PT_ID':
                        for p in self.plans:
                            for s in self.sections:
                                for t in self.dct_sect[s]:
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, str(t))
                                    if not os.path.exists(path_res):
                                        os.makedirs(path_res)
                                    dfs=[]
                                    for y in self.years:
                                        df_year=pd.read_csv(os.path.join(self.ISEE_RES, PI, p, s, str(y), f'{PI}_{y}_{s}_{t}.csv'), sep=self.sep)
                                        dfs.append(df_year)
                                    df_all=df_year=pd.concat(dfs, ignore_index=True)
                                    if len(stats)==1:
                                        if stats[0]==['sum']:
                                            df_all_all=df_all.groupby(['PT_ID'], as_index=False).sum()
                                        elif stats[0]==['mean']:
                                            df_all_all=df_all.groupby(['PT_ID'], as_index=False).mean()
                                    if len(stats)>1:
                                        df_all_sum=df_all.groupby(['PT_ID'], as_index=False).sum()
                                        df_all_mean=df_all.groupby(['PT_ID'], as_index=False).mean()
                                        df_all_all=df_all_sum.merge(df_all_mean, on='PT_ID', suffixes=('_sum', '_mean'), validate='one_to_one')
                                    df_all_all.to_csv(os.path.join(path_res, f'{PI}_{AGG_TIME}_{p}_{s}_{t}_PT_ID_{min(self.years)}_{max(self.years)}.csv'), sep=self.sep, index=False)

                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()
                        
                elif AGG_TIME=='QM':
                    pass
                            
                else:
                    pass
            
            
de=POST_PROCESS_2D(cfg.pis, cfg.plans, cfg.sections, cfg.years, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, cfg.dct_sect)  
    
for pi in de.pis:

    de.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'], ['sum', 'mean']) 
    
quit()
 
 
#===============================================================================
# res_folder=fr'F:\DEM_GLAMM\Dashboard\ISEE_RESULTS\ESLU_2D'
# plans=['Alt_1', 'Alt_2', 'Baseline']
#  
# years=list(range(1926,2017))
#  
# for plan in plans:
#     folder_plan=os.path.join(res_folder, plan)
#      
#     liste_files=[]
#     for y in years:
#         for root, dirs, files in os.walk(folder_plan):
#             for name in files:
#                 liste_files.append(os.path.join(root, name))
#              
#         liste_file_year=[f for f in liste_files if str(y) in f]
#          
#         new_year_path=os.path.join(folder_plan, str(y))
#         os.makedirs(new_year_path, exist_ok=True)
#          
#         for file_year in liste_file_year:
#             src=file_year
#             dst=os.path.join(new_year_path,file_year.split('\\')[-1])
#             print(dst)
#             shutil.copy(src, dst)
# quit()
#===============================================================================
             
        
        #=======================================================================
        # for csv in liste_file_year:
        #     df_temp=pd.read_csv(csv, sep=self.sep)
        #     liste_df.append(df_temp)
        # df_year=pd.concat(liste_df, ignore_index=True)
        #=======================================================================


#===============================================================================
# folder=r"F:\DEM_GLAMM\Dashboard\ISEE_RESULTS\ESLU_2D"
#  
# liste_files=[]
# for root, dirs, files in os.walk(folder):
#     for name in files:
#         liste_files.append(os.path.join(root, name))
#  
# print(len(liste_files))
#  
# for f in liste_files:
#     dest=f.replace('Tile_', '')
#     os.rename(f, dest)
#     
#===============================================================================
    
 #==============================================================================
 #    sect_list=f.split('_')[-4:-2]
 #    sect_name=sect_list[0]+'_'+sect_list[1]
 #    print(sect_name)
 #    if sect_name=='Section_40':
 #        dest=f.replace(sect_name, 'LKO_CAN')
 #        print(dest)
 #        os.rename(f, dest)
 #    elif sect_name=='Section_50':
 #        dest=f.replace(sect_name, 'USL_CAN')
 #        print(dest)
 #        os.rename(f, dest)
 #    else:
 #        print('already renamed!')
 # 
 #==============================================================================
    #src=f
    #dst=

#===============================================================================
# for pi in pis: 
#     path_pi=os.path.join(res_folder, pi)
#     count_plan=0
#     for plan in plans:
#         print(plan)
#         count_plan+=1
#         for section in sections:
# #===============================================================================
# #             src=os.path.join(res_folder, pi, plan, f'Section_{section}')
# #             dst=os.path.join(mock_folder, pi, plan, f'Section_{section}')
# #             shutil.copytree(src, dst, dirs_exist_ok=True)
# # quit()
# #===============================================================================
#             #===================================================================
#             # liste=os.listdir(os.path.join(res_folder, pi, plan, f'Section_{section}'))
#             # print(liste)
#             # liste2=[]
#             #===================================================================
# #===============================================================================
# # 
# #             for tile in liste2:
# #                 
# #                 tile_path=os.path.join(res_folder, pi, plan, f'Section_{section}', tile)
# #===============================================================================
#             for year in years:
#                 year_path=os.path.join(mock_folder, pi, plan, f'Section_{section}', str(year))
#                 #print(year_path)
#                 liste=os.listdir(year_path)
#                 for f in liste:
#                     path=os.path.join(year_path, f)
#                     #path2=path.replace('.csv', 'TEST.csv')
#                     #print(path)
#                     df=pd.read_csv(path, sep=';')
#                     #print(list(df))
#                     if 'VAR1' in list(df):
#                         continue
#                     else:  
#                         df_clean=df[['PT_ID','HSI','PMI','SED']]
#                         #df_clean=df[['PT_ID','VAR1','VAR2','VAR3']]
#                         df_clean=df_clean.rename(columns={"HSI": "VAR1", "PMI": "VAR2", "SED":'VAR3'})
#                         df_clean.to_csv(path, sep=';', index=None)
#                         if count_plan==1:
#                             df_XY=df[['PT_ID', 'XVAL', 'YVAL']]
#                             name=f'ISEE_tile_{f.split("_")[-1]}'
#                             df_XY.to_csv(os.path.join(mock_folder, 'Tiles', name), sep=';', index=None)
#                             #print(path)
#                             #print(os.path.join(mock_folder, 'Tile', name))
# quit()
#===============================================================================

#===============================================================================
#                     
#                     src=os.path.join(tile_path, f'{pi}_CAN_{year}_Section_{section}_{tile}.csv')
#                     dst=os.path.join(res_folder, pi, plan, f'Section_{section}', str(year), f'{pi}_CAN_{year}_Section_{section}_{tile}.csv')
#                     shutil.copy(src,dst)
# quit()
#  
#  
#             for year in years:
#                 os.makedirs(os.path.join(res_folder, pi, plan, f'Section_{section}', str(year)))
# quit() 
#===============================================================================