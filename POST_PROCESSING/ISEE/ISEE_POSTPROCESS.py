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
                t=feather.split('_')[-2]
                df_t=pd.read_feather(fr"{self.ISEE_RES}\Tiles\ISEE_GRID_tile_{t}.feather")
                df_t=df_t[['PT_ID', 'X_COORD', 'Y_COORD']]
                #df_temp=df_temp[[self.id_column_name, str(y)]]
                df_temp=df_temp[[PI_CFG.id_column_name, str(y)]]
                #df_temp=df_temp.merge(df_t, on=self.id_column_name, how='left', suffixes=('', ''))
                df_temp=df_temp.merge(df_t, on=PI_CFG.id_column_name, how='left', suffixes=('', ''))
                
                liste_df.append(df_temp)
            df_y=pd.concat(liste_df, ignore_index=True, axis=0)            
            if count_y==1:
                df_main=df_y
            else:
                #df_main=df_main.merge(df_y, on=[self.id_column_name,'X_COORD','Y_COORD'], how='outer', suffixes=('', ''))
                df_main=df_main.merge(df_y, on=[PI_CFG.id_column_name,'X_COORD','Y_COORD'], how='outer', suffixes=('', ''))
        
        print(df_main.head())
        df_main.to_feather(os.path.join(path_res, res_name))

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE, stats):
        
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
            
            for feather in liste_files:
                df_temp=pd.read_feather(feather)
                df_temp=df_temp.loc[df_temp['SECTION']==s]
                
                tiles=df_temp['TILE'].unique()
                

                
                dfs_temp_t=[]
                for t in tiles:
                    print(t)
                    df_temp_t=df_temp.loc[df_temp['TILE']==t]
                    print(list(df_temp_t))
                    df_temp_t=df_temp_t[['PT_ID', var]]
                    df_t=pd.read_feather(fr"{self.ISEE_RES}\Tiles\ISEE_GRID_tile_{t}.feather")
                    df_t=df_t[['PT_ID', 'X_COORD', 'Y_COORD']]
                    
                    print(df_temp.head())
                    print(df_t.head())
                    
                    df_temp_t=df_temp_t.merge(df_t, on=PI_CFG.id_column_name, how='left', suffixes=('', ''))
                    dfs_temp_t.append(df_temp_t)
                    
                df_temp=pd.concat(dfs_temp_t, ignore_index=True, axis=0)
                print(df_temp.head())
   
                df_temp[str(y)]=df_temp[var]
                df_temp=df_temp[[PI_CFG.id_column_name, str(y), 'X_COORD', 'Y_COORD']]
                liste_df.append(df_temp)                
            df_y=pd.concat(liste_df, ignore_index=True, axis=0)
            
            if count_y==1:
                df_main=df_y
            else:
                df_main=df_main.merge(df_y, on=[PI_CFG.id_column_name,'X_COORD','Y_COORD'], how='outer', suffixes=('', ''))
            print(len(df_main))
            
        df_main.to_feather(os.path.join(path_res, res_name))

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE, stats):
        
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
                var_sum=var+'_sum'
                df_space[var_sum]=df_space[var]
                columns.append(var_sum)
            df_space=df_space[columns]
        
        df_space=df_space.reset_index()                               
        df_space.to_feather(os.path.join(path_res, res_name))

    def agg_1D_space(self, PI, AGGS_TIME, AGGS_SPACE, stats):
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

   
for pi in tiled.pis:
    print(pi)
    tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'], ['sum']) 
    #tiled.agg_2D_space(pi, ['YEAR'], ['PT_ID'], ['sum'])
           
for pi in not_tiled.pis:  
    print(pi)
    not_tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'], ['sum']) 
    #not_tiled.agg_2D_space(pi, ['YEAR'], ['PT_ID'], ['sum'])
        
#===============================================================================
# for pi in pi_1D.pis:
#     print(pi)
#     pi_1D.agg_1D_space(pi, ['YEAR'], ['PLAN', 'SECTION'], ['sum'])
#===============================================================================
          
     

quit()


 

'''
Bunch of messy piece of codes to manipulate old Richelieu River data into ISEE-GLAM data format
'''
               
               
#===============================================================================
# tiles_folder=r'M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\Tiles'
#      
# liste=os.listdir(tiles_folder)
#      
# for f in liste:
#     #path=fr"M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\Tiles\ISEE_tile_47.feather"
#         
#     path=fr'{tiles_folder}\{f}'
#     dst=path.replace('.csv', '.feather')
#     os.rename(path, dst)
# quit()  
#===============================================================================
    

#===============================================================================
# path=r"M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\Tiles\ISEE_GRID_Tile_40.feather"
# df=pd.read_feather(path)
# df.to_csv(path.replace('feather', 'csv'), index=None)
# quit()
#===============================================================================

#===============================================================================
# folder=fr"M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\Tiles"
# liste_files=[]
# for root, dirs, files in os.walk(folder):
#     for name in files:
#         liste_files.append(os.path.join(root, name))
#     
# for f in liste_files:
#     df=pd.read_csv(f, sep=';')
#     print(list(df))
#     df=df[['PT_ID', 'XVAL', 'YVAL']]
#     t=f.split('_')[-1].replace('.csv', '')
#     print(t)
#     #df=df.drop(columns=['index'])
#     dst=fr'{folder}\ISEE_tile_{t}.feather'
#     df.to_feather(dst)
# quit()
#===============================================================================
    
    
#===============================================================================
# tiles_folder=r'M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\Tiles'
#      
# liste=os.listdir(tiles_folder)
#      
# for f in liste:
#     #path=fr"M:\ISEE_Dashboard\DATA\ISEE\ISEE_RAW_DATA\Tiles\ISEE_tile_47.feather"
#         
#     path=fr'{tiles_folder}\{f}'
#     dst=path.replace('.csv', '.feather')
#       
#     #t=path.split('_')[-1].replace('.feather', '')
#     #t=int(t)
#       
#     #dst=path.replace('.feather', '.csv' )
#         
#     df=pd.read_csv(path, sep=';')
#       
#     #df['PT_ID']=1000000*t+df['PT_ID']
#        
#     print(df.head())
#    
#     df=df[['PT_ID', 'XVAL', 'YVAL']]
#          
#     utm=pyproj.CRS('EPSG:32618')
#     utm2=pyproj.CRS('EPSG:2958')
#     coord=pyproj.CRS('EPSG:4329')
#          
#     transformer = Transformer.from_crs(utm, utm2)
#                       
#     x_pts=df['XVAL']
#     y_pts=df['YVAL']
#          
#         
#     x_proj, y_proj=transformer.transform(x_pts, y_pts)
#     #===========================================================================
#     # df['X_UTM2']= x_proj
#     # df['Y_UTM2']= y_proj
#     # 
#     #===========================================================================
#     transformer2 = Transformer.from_crs(utm2, coord)
#      ## it works but strange!! ##  ## retested in 2023-11-13 and still seems to be what is working...
#     y_coord, x_coord = transformer2.transform(x_proj, y_proj)
#         
#     df['X_COORD']= x_coord
#     df['Y_COORD']= y_coord
#         
#         
#     df.to_feather(dst)
#     #print(df.head())
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
    

#===============================================================================
# for file in liste_files:
#     df=pd.read_feather(file, sep=';')
#     df=df[['PT_ID',    'VAR1',    'VAR2',    'VAR3',    'SECTION',    'TILE']]
#     df.to_feather(file, sep=';', index=None)
# quit()
#===============================================================================

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
        # for feather in liste_file_year:
        #     df_temp=pd.read_feather(feather, sep=self.sep)
        #     liste_df.append(df_temp)
        # df_year=pd.concat(liste_df, ignore_index=True)
        #=======================================================================


#===============================================================================
# folder=r'M:\ISEE_Dashboard\ISEE_POST_PROCESS\SAUV_2D'
#   
# liste_files=[]
# for root, dirs, files in os.walk(folder):
#     for name in files:
#         liste_files.append(os.path.join(root, name))
#   
# print(len(liste_files))
#   
# for f in liste_files:
#     dest=f.replace('ESLU', 'SAUV')
#     os.rename(f, dest)
# quit()
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
#                     #path2=path.replace('.feather', 'TEST.feather')
#                     #print(path)
#                     df=pd.read_feather(path, sep=';')
#                     #print(list(df))
#                     if 'VAR1' in list(df):
#                         continue
#                     else:  
#                         df_clean=df[['PT_ID','HSI','PMI','SED']]
#                         #df_clean=df[['PT_ID','VAR1','VAR2','VAR3']]
#                         df_clean=df_clean.rename(columns={"HSI": "VAR1", "PMI": "VAR2", "SED":'VAR3'})
#                         df_clean.to_feather(path, sep=';', index=None)
#                         if count_plan==1:
#                             df_XY=df[['PT_ID', 'XVAL', 'YVAL']]
#                             name=f'ISEE_tile_{f.split("_")[-1]}'
#                             df_XY.to_feather(os.path.join(mock_folder, 'Tiles', name), sep=';', index=None)
#                             #print(path)
#                             #print(os.path.join(mock_folder, 'Tile', name))
# quit()
#===============================================================================

#===============================================================================
#                     
#                     src=os.path.join(tile_path, f'{pi}_CAN_{year}_Section_{section}_{tile}.feather')
#                     dst=os.path.join(res_folder, pi, plan, f'Section_{section}', str(year), f'{pi}_CAN_{year}_Section_{section}_{tile}.feather')
#                     shutil.copy(src,dst)
# quit()
#  
#  
#             for year in years:
#                 os.makedirs(os.path.join(res_folder, pi, plan, f'Section_{section}', str(year)))
# quit() 
#===============================================================================


                    #===========================================================
                    # elif AGG_SPACE=='PT_ID':
                    #     for p in self.plans:
                    #         for s in self.sections:
                    #             for t in self.dct_sect[s]:
                    #                 path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, str(t))
                    #                 if not os.path.exists(path_res):
                    #                     os.makedirs(path_res)
                    #                 dfs=[]
                    #                 for y in self.years:
                    #                     df_year=pd.read_feather(os.path.join(self.ISEE_RES, PI, p, s, str(y), f'{PI}_{y}_{s}_{t}.feather'), sep=self.sep)
                    #                     dfs.append(df_year)
                    #                 df_all=df_year=pd.concat(dfs, ignore_index=True)
                    #                 
                    #                 if len(stats)==1:
                    #                     if stats[0]==['sum']:
                    #                         df_all_all=df_all.groupby(['PT_ID'], as_index=False).sum()
                    #                     elif stats[0]==['mean']:
                    #                         df_all_all=df_all.groupby(['PT_ID'], as_index=False).mean()
                    #                 if len(stats)>1:
                    #                     df_all_sum=df_all.groupby(['PT_ID'], as_index=False).sum()
                    #                     df_all_mean=df_all.groupby(['PT_ID'], as_index=False).mean()
                    #                     df_all_all=df_all_sum.merge(df_all_mean, on=['PT_ID'], suffixes=('_sum', '_mean'), validate='one_to_one')
                    #                 df_all_all.to_feather(os.path.join(path_res, f'{PI}_{AGG_TIME}_{p}_{s}_{t}_PT_ID_{min(self.years)}_{max(self.years)}.feather'), sep=self.sep, index=False)
                    #===========================================================
                    
                    #===========================================================
                    # elif AGG_SPACE=='PT_ID':
                    #     for p in self.plans:
                    #         print(p)
                    #         path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                    #         if not os.path.exists(path_res):
                    #             os.makedirs(path_res)
                    #         dfs=[]
                    #         for y in self.years:
                    #             df_year=pd.read_feather(os.path.join(self.ISEE_RES, PI, p, f'{PI}_{p}_{y}.feather'), sep=self.sep)
                    #             dfs.append(df_year)
                    #         df_all=pd.concat(dfs, ignore_index=True)
                    #         if len(stats)==1:
                    #             if stats[0]==['sum']:
                    #                 df_all_all=df_all.groupby(['PT_ID', 'TILE', 'SECTION'], as_index=False).sum()
                    #             elif stats[0]==['mean']:
                    #                 df_all_all=df_all.groupby(['PT_ID', 'TILE', 'SECTION'], as_index=False).mean()
                    #         if len(stats)>1:
                    #             df_all_sum=df_all.groupby(['PT_ID', 'TILE', 'SECTION'], as_index=False).sum()
                    #             df_all_mean=df_all.groupby(['PT_ID', 'TILE', 'SECTION'], as_index=False).mean()
                    #             df_all_all=df_all_sum.merge(df_all_mean, on=['PT_ID', 'TILE', 'SECTION'], suffixes=('_sum', '_mean'), validate='one_to_one')
                    #         df_all_all.to_feather(os.path.join(path_res, f'{PI}_{AGG_TIME}_{p}_PT_ID_{min(self.years)}_{max(self.years)}.feather'), sep=self.sep, index=False)
                    #===========================================================