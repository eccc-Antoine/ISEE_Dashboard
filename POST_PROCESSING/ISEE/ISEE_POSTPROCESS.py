import os
import pandas as pd
import geopandas as gpd
import shutil
import importlib
import POST_PROCESSING.ISEE.CFG_POST_PROCESS_ISEE as cfg
from pyproj import transform, Proj
import pyproj
from pyproj import Transformer



class POST_PROCESS_2D_tiled:
    
    #def __init__(self, pis, plans, sections, years, ISEE_RES, POST_PROCESS_RES, sep, dct_sect, id_column_name):
    def __init__(self, pis, ISEE_RES, POST_PROCESS_RES, sep):

        self.pis=pis
        #self.plans=plans
        #self.sections=sections
        #self.years=years
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        #self.dct_sect=dct_sect
        #self.id_column_name=id_column_name
           
    def agg_YEAR(self, folder_space, y):  

        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        liste_df=[]
        liste_file_year=[f for f in liste_files if str(y) in f]
        for feather in liste_file_year:
            df_temp=pd.read_feather(feather)
            liste_df.append(df_temp)
        df_year=pd.concat(liste_df, ignore_index=True)
        return df_year
    
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG):
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        #df_space[AGG_TIME]=self.years
        df_space[AGG_TIME]=PI_CFG.available_years
        if not os.path.exists(path_res):
            os.makedirs(path_res)
        #for y in self.years:
        for y in PI_CFG.available_years:
            if AGG_SPACE == 'PLAN' or AGG_SPACE == 'SECTION':               
                df_year=self.agg_YEAR(agg_year_param, y)
            elif AGG_SPACE == 'TILE':
                path_feather_year2=path_feather_year.replace('foo', str(y))
                df_year=pd.read_feather(path_feather_year2)
            for var in list_var:
                for stat in stats:
                    if stat=='sum':
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].sum()
                    elif stat=='mean':
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].mean()
                    else:
                        print('STAT value provided is unavailable')
        df_space=df_space.reset_index()
        df_space.to_feather(os.path.join(path_res, res_name))
    
    def AGG_PT_ID_ALL_YEARS(self, PI, p, s, var, path_res, res_name, PI_CFG):
        count_y=0
        #for y in self.years:
        for y in PI_CFG.available_years:
            count_y+=1
            liste_files=[]
            folder_space=os.path.join(self.ISEE_RES, PI,p, s, str(y))
            for root, dirs, files in os.walk(folder_space):
                for name in files:
                    liste_files.append(os.path.join(root, name))
            liste_df=[]
            #liste_file_year=[f for f in liste_files if str(y) in f]
            for feather in liste_files:
                df_temp=pd.read_feather(feather)
                df_temp[str(y)]=df_temp[var]
                
                
                
                ##un comment if there is not lat lon in raw results
                #===============================================================
                #t=feather.split('_')[-2]
                # df_t=pd.read_feather(fr"{self.ISEE_RES}\Tiles\ISEE_GRID_tile_{t}.feather")
                # df_t=df_t[['PT_ID', 'X_COORD', 'Y_COORD']]
                # #df_temp=df_temp[[self.id_column_name, str(y)]]
                # df_temp=df_temp[[PI_CFG.id_column_name, str(y)]]
                # #df_temp=df_temp.merge(df_t, on=self.id_column_name, how='left', suffixes=('', ''))
                # df_temp=df_temp.merge(df_t, on=PI_CFG.id_column_name, how='left', suffixes=('', ''))
                #===============================================================
                
                df_temp=df_temp[[PI_CFG.id_column_name, str(y), 'LAT', 'LON']]
                
                liste_df.append(df_temp)
            df_y=pd.concat(liste_df, ignore_index=True, axis=0)            
            if count_y==1:
                df_main=df_y
            else:
                #df_main=df_main.merge(df_y, on=[self.id_column_name,'X_COORD','Y_COORD'], how='outer', suffixes=('', ''))
                df_main=df_main.merge(df_y, on=[PI_CFG.id_column_name,'LAT','LON'], how='outer', suffixes=('', ''))
        
        print(df_main.head())
        df_main.to_feather(os.path.join(path_res, res_name))

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata 
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION', 'TILE']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean'] 
        '''
        
        pi_module_name=f'CFG_{PI}'
        PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        
        for AGG_TIME in AGGS_TIME:
            for AGG_SPACE in AGGS_SPACE:  
                print(AGG_SPACE)
                #===============================================================
                # pi_module_name=f'CFG_{PI}'
                # PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
                #===============================================================
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)
                        
                if AGG_TIME=='YEAR':
                    if AGG_SPACE=='PLAN':
                        #for space in self.plans:
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            print(space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG)
                              
                    elif AGG_SPACE=='SECTION':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for space in self.sections:
                            for space in PI_CFG.available_sections:
                                print(space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p, space)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG)

                    elif AGG_SPACE=='TILE':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for s in self.sections:
                            for s in PI_CFG.available_sections: 
                                #for space in self.dct_sect[s]:
                                for space in PI_CFG.dct_tile_sect[s]:
                                    print(space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                    path_feather_year=os.path.join(self.ISEE_RES, PI, p, s, 'foo' , f'{PI}_{p}_{s}_{space}_foo.feather')
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, '', path_feather_year, PI_CFG)
                    
                    elif AGG_SPACE=='PT_ID':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for s in self.sections: 
                            for s in PI_CFG.available_sections:                                
                                for var in list(PI_CFG.dct_var.keys()):
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                    if not os.path.exists(path_res):
                                        os.makedirs(path_res)
                                    res_name=f'{var}_{PI}_{AGG_TIME}_{p}_{s}_{AGG_SPACE}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                    self.AGG_PT_ID_ALL_YEARS(PI, p, s, var, path_res, res_name, PI_CFG)
                    
                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()
                        
                elif AGG_TIME=='QM':
                    ### NOT coded yet!!
                    pass
                            
                else:
                    pass
                
class POST_PROCESS_2D_not_tiled:
    
    #def __init__(self, pis, plans, sections, years, ISEE_RES, POST_PROCESS_RES, sep, dct_sect, id_column_name):
    def __init__(self, pis, ISEE_RES, POST_PROCESS_RES, sep):

        self.pis=pis
        #self.plans=plans
        #self.sections=sections
        #self.years=years
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        #self.dct_sect=dct_sect
        #self.id_column_name=id_column_name
        
    def agg_YEAR(self, folder_space, y):  
        
        print(folder_space)
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        liste_df=[]
        liste_file_year=[f for f in liste_files if str(y) in f]
        for feather in liste_file_year:
            df_temp=pd.read_feather(feather)
            liste_df.append(df_temp)
        df_year=pd.concat(liste_df, ignore_index=True)
        return df_year
    
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG):
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        #df_space[AGG_TIME]=self.years
        df_space[AGG_TIME]=PI_CFG.available_years
        if not os.path.exists(path_res):
            os.makedirs(path_res)
        #for y in self.years:
        for y in PI_CFG.available_years:
            if AGG_SPACE == 'PLAN':               
                df_year=self.agg_YEAR(agg_year_param, y)
            
            elif AGG_SPACE == 'SECTION':
                df_year=self.agg_YEAR(agg_year_param, y)
                df_year=df_year.loc[df_year['SECTION']==space]
            
            elif AGG_SPACE == 'TILE':
                df_year=self.agg_YEAR(agg_year_param, y)
                df_year=df_year.loc[df_year['TILE']==int(space)]
            for var in list_var:
                for stat in stats:
                    if stat=='sum':
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].sum()
                    elif stat=='mean':
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].mean()
                    else:
                        print('STAT value provided is unavailable') 
                        
        df_space=df_space.reset_index()  
        df_space.to_feather(os.path.join(path_res, res_name))
    
    def AGG_PT_ID_ALL_YEARS(self, PI, p, s, var, path_res, res_name, PI_CFG):
        count_y=0
        #for y in self.years:
        #for y in [1990, 1991]:
        for y in PI_CFG.available_years:
            count_y+=1
            liste_files=[]
            folder_space=os.path.join(self.ISEE_RES, PI,p)
            for root, dirs, files in os.walk(folder_space):
                for name in files:
                    year=name.split('_')[-1].replace('.feather', '')
                    if year==str(y):
                        liste_files.append(os.path.join(root, name))
            liste_df=[]
            
            #print(len(liste_files))
            
            for feather in liste_files:
                #print(feather)
                df_temp=pd.read_feather(feather)
                df_temp=df_temp.loc[df_temp['SECTION']==s]
                

                #===============================================================
                # tiles=df_temp['TILE'].unique()
                # #print(tiles)
                # tiles2=df_temp['TILE'].astype(int).unique()
                # #print(tiles2)
                # 
                # dfs_temp_t=[]
                # for t in tiles:
                #     #print(t)
                #     
                #     ##uncomment if ther is no lat lon in raw data files
                #     #===========================================================
                #     # df_temp_t=df_temp.loc[df_temp['TILE']==t]
                #     # print(list(df_temp_t))
                #     # df_temp_t=df_temp_t[['PT_ID', var]]
                #     # df_t=pd.read_feather(fr"{self.ISEE_RES}\Tiles\ISEE_GRID_tile_{t}.feather")
                #     # df_t=df_t[['PT_ID', 'X_COORD', 'Y_COORD']]
                #     # 
                #     # print(df_temp.head())
                #     # print(df_t.head())
                #     # 
                #     # df_temp_t=df_temp_t.merge(df_t, on=PI_CFG.id_column_name, how='left', suffixes=('', ''))
                #     #===========================================================
                #     
                #     df_temp_t=df_temp.loc[df_temp['TILE']==t]
                #     print(df_temp_t.head())
                #     quit()
                #     
                #     dfs_temp_t.append(df_temp_t)
                #     
                #     
                # df_temp=pd.concat(dfs_temp_t, ignore_index=True, axis=0)
                # #print(df_temp.head())
                #===============================================================
                
                #===============================================================
                # print(df_temp.head())
                # 
                # print(list(df_temp))
                # print(len(df_temp))
                # print(len(df_temp['PT_ID'].unique()))
                # print(var)
                # 
                #===============================================================
                df_temp=df_temp.drop_duplicates(subset=['PT_ID'])
                
                df_temp[str(y)]=df_temp[var]
                df_temp=df_temp[[PI_CFG.id_column_name, str(y), 'LAT', 'LON']]
                
                #print(len(df_temp))
                
                liste_df.append(df_temp)      
                #print(len(liste_df))          
            df_y=pd.concat(liste_df, ignore_index=True, axis=0)
            
            print(len(df_y))
            #print(df_y.head())
            
            if count_y==1:
                df_main=df_y
            else:
                df_main=df_main.merge(df_y, on=[PI_CFG.id_column_name,'LAT','LON'], how='outer', suffixes=('', ''))
            print(len(df_main))
        
        #print(df_main.head())
        #print(len(df_main))
        #print(len(df_main['PT_ID'].unique()))
        df_main=df_main.reset_index()
        df_main.to_feather(os.path.join(path_res, res_name))

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata 
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION', 'TILE']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean'] 
        '''
        pi_module_name=f'CFG_{PI}'
        PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        
        
        for AGG_TIME in AGGS_TIME:
            for AGG_SPACE in AGGS_SPACE:  
                print(AGG_SPACE)
                #===============================================================
                # pi_module_name=f'CFG_{PI}'
                # PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
                #===============================================================
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)
                        
                if AGG_TIME=='YEAR':
                    if AGG_SPACE=='PLAN':
                        #for space in self.plans:
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            print(space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'                           
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG)
                              
                    elif AGG_SPACE=='SECTION':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for space in self.sections:
                            for space in PI_CFG.available_sections:
                                print(p, space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)                                
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG)

                    elif AGG_SPACE=='TILE':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for s in self.sections:
                            for s in PI_CFG.available_sections: 
                                #for space in self.dct_sect[s]:
                                for space in PI_CFG.dct_tile_sect[s]:
                                    print(p, s, space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                    agg_year_param=os.path.join(self.ISEE_RES, PI, p)
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG)
                   
                    elif AGG_SPACE=='PT_ID':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for s in self.sections: 
                            for s in PI_CFG.available_sections:                             
                                for var in list(PI_CFG.dct_var.keys()):
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                    if not os.path.exists(path_res):
                                        os.makedirs(path_res)
                                    res_name=f'{var}_{PI}_{AGG_TIME}_{p}_{s}_{AGG_SPACE}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                    self.AGG_PT_ID_ALL_YEARS(PI, p, s, var, path_res, res_name, PI_CFG)

                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()
                        
                elif AGG_TIME=='QM':
                    ### NOT coded yet!!
                    pass
                            
                else:
                    pass
                
class POST_PROCESS_1D:
    
    #def __init__(self, pis, plans, sections, years, ISEE_RES, POST_PROCESS_RES, sep, dct_sect):
    def __init__(self, pis,ISEE_RES, POST_PROCESS_RES, sep):

        self.pis=pis
        #self.plans=plans
        #self.sections=sections
        #self.years=years
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        #self.dct_sect=dct_sect
           
    def agg_YEAR(self, folder_space):  
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        df_year=pd.DataFrame()
        liste_df=[]
        for feather in liste_files:
            df_temp=pd.read_feather(feather)
            liste_df.append(df_temp)
        df_year=pd.concat(liste_df, ignore_index=True)
        
        return df_year
    
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG):
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        #df_space[AGG_TIME]=self.years
        df_space[AGG_TIME]=PI_CFG.available_years
        if not os.path.exists(path_res):
            os.makedirs(path_res)
        if AGG_SPACE == 'PLAN':               
            df_year=self.agg_YEAR(agg_year_param)
            for stat in stats:
                if stat=='sum':
                    df_space_sum=df_year.groupby(['YEAR'], as_index=False).sum()
                elif stat=='mean':
                    df_space_mean=df_year.groupby(['YEAR'], as_index=False).mean()
    
            if len(stats)>1:
                df_space=df_space_sum.merge(df_space_mean, on=['YEAR'], suffixes=('_sum', '_mean'), validate='one_to_one')
            elif stats[0]=='sum':
                df_space=df_space_sum
            elif stats[0]=='mean':
                df_space=df_space_mean
            else:
                print('STAT value provided is unavailable')
                       
        elif AGG_SPACE == 'SECTION':
            df_space=self.agg_YEAR(agg_year_param)
            columns=['YEAR']
            for var in list_var:
                stats=PI_CFG.var_agg_stat[var]
                for stat in stats:
                    var_stat=var+f'_{stat}'
                    df_space[var_stat]=df_space[var]
                    columns.append(var_stat)
            df_space=df_space[columns]
        
        df_space=df_space.reset_index()                               
        df_space.to_feather(os.path.join(path_res, res_name))

    def agg_1D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata 
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean'] 
        '''
        
        pi_module_name=f'CFG_{PI}'
        PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        
        for AGG_TIME in AGGS_TIME:
            for AGG_SPACE in AGGS_SPACE:  
                print(AGG_SPACE)
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)
                        
                if AGG_TIME=='YEAR':
                    if AGG_SPACE=='PLAN':
                        #for space in self.plans:
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            print(space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'                           
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG )
                              
                    elif AGG_SPACE=='SECTION':
                        #for p in self.plans:
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            #for space in self.sections:
                            for space in PI_CFG.available_sections:
                                print(p, space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)                                
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(PI_CFG.available_years)}_{max(PI_CFG.available_years)}.feather'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p, space)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG )

                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()
                        
                elif AGG_TIME=='QM':
                    ### NOT coded yet!!
                    pass
                            
                else:
                    pass
            
            
#===============================================================================
# tiled=POST_PROCESS_2D_tiled(cfg.pis_2D_tiled, cfg.plans, cfg.sections, cfg.years, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, cfg.dct_sect, cfg.id_column_name) 
# 
# not_tiled=POST_PROCESS_2D_not_tiled(cfg.pis_2D_not_tiled, cfg.plans, cfg.sections, cfg.years, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, cfg.dct_sect, cfg.id_column_name)  
#  
# pi_1D=POST_PROCESS_1D(cfg.pis_1D, cfg.plans, cfg.sections, cfg.years, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, cfg.dct_sect)
#===============================================================================

tiled=POST_PROCESS_2D_tiled(cfg.pis_2D_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep) 

not_tiled=POST_PROCESS_2D_not_tiled(cfg.pis_2D_not_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)  
 
pi_1D=POST_PROCESS_1D(cfg.pis_1D, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

   
#===============================================================================
# for pi in tiled.pis:
#     print(pi)
#     #tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID']) 
#     tiled.agg_2D_space(pi, ['YEAR'], ['PT_ID'])
#===============================================================================
             
#===============================================================================
# for pi in not_tiled.pis:  
#     print(pi)
#     not_tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID']) 
#     #not_tiled.agg_2D_space(pi, ['YEAR'], ['PT_ID'])
#           
#===============================================================================
         
        
for pi in pi_1D.pis:
    print(pi)
    pi_1D.agg_1D_space(pi, ['YEAR'], ['PLAN', 'SECTION'])
             
quit()


               
