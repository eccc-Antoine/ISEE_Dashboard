import os
import pandas as pd
import geopandas as gpd
import shutil
import importlib
import POST_PROCESSING.GLRRM.CFG_POST_PROCESS_GLRRM as cfg
import POST_PROCESSING.ISEE.CFG_POST_PROCESS_ISEE as ISEE_cfg
import sqlite3
import numpy as np

class POST_PROCESS_exp:
    
    def __init__(self, GLRRM_RES, POST_PROCESS_RES, POST_PROCESS_ISEE, sep):

        self.GLRRM_RES=GLRRM_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.POST_PROCESS_ISEE=POST_PROCESS_ISEE
        self.sep=sep
    
    def list_exps(self, ):
        experiments=os.listdir(exps.GLRRM_RES)
        #=======================================================================
        # con = sqlite3.connect(exps.GLRRM_RES)
        # df = pd.read_sql_query(f"SELECT * from {cfg.exp_table_name}", con)
        # experiments=list(df[cfg.exp_col_name])
        # con.close()
        #=======================================================================
        return  experiments

    def AGG_SPACE(self,  EXP, AGGS_TIME, AGGS_SPACE, stats, PIS):
        
        '''
        EXP = experience name
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM']
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'LOCATION']
        stats = stats to compute whwne aggregating results per year ['mean', 'max', 'min']
        PIS= List of PIS for which we want to produce results based on 1D equation
        '''
        
        con = sqlite3.connect(exps.GLRRM_RES)
        query=f"SELECT * from {cfg.output_table_name} where {cfg.exp_col_name} ='{EXP}'"
        print(query)
        df = pd.read_sql_query(query, con)
        #path=os.path.join(exps.GLRRM_RES, EXP, 'outputs')
        #df=pd.read_csv(path)
        

        for AGG_TIME in AGGS_TIME:
            
            print(AGG_TIME)
            
            for AGG_SPACE in AGGS_SPACE:
                print(AGG_SPACE)
                
                if AGG_SPACE=='LOCATION':
                    locations=list(df[cfg.location_col_name].unique())
                    for loc in locations:
                        print(loc)
                        df_loc=df.loc[df[cfg.location_col_name]==loc]
                        df_loc['values'].loc[df_loc['kind']=='sym']=np.nan
                        df_loc['values']=df_loc['values'].astype('float64')
                        df_loc= df_loc[['year', 'qm48', 'values', 'location', 'kind', 'units']]
                        res_name=fr'{loc}_{EXP}_{AGG_TIME}.feather'
                        res_folder=os.path.join(cfg.post_process_folder, EXP, AGG_TIME)
                        path_res=os.path.join(res_folder, res_name)
                        if AGG_TIME=='QM':
                            if not os.path.exists(res_folder):
                                os.makedirs(res_folder)
                            df_loc=df_loc.reset_index()
                            df_loc.to_feather(path_res)
 
                        elif AGG_TIME=='YEAR':
                            df_loc_year=df_loc.groupby(['year','location', 'kind', 'units'], as_index=False).mean()
                            df_loc_year=df_loc_year[['year','location', 'kind', 'units']]
                            for s in stats:
                                if s =='mean':
                                    df_loc_year_s=df_loc.groupby(['year','location', 'kind', 'units'], as_index=False).mean()
                                elif s == 'max':
                                    df_loc_year_s=df_loc.groupby(['year','location', 'kind', 'units'], as_index=False).max()
                                elif s=='min':
                                    df_loc_year_s=df_loc.groupby(['year','location', 'kind', 'units'], as_index=False).min()
                                else:
                                    print('stat in input is unavailable')
                                
                                df_loc_year_s=df_loc_year_s[['year', 'values']]
                                df_loc_year_s=df_loc_year_s.rename(columns={"values": f"values_{s}"})
                                df_loc_year=df_loc_year.join(df_loc_year_s[f'values_{s}'])
                            
                            if not os.path.exists(res_folder):
                                os.makedirs(res_folder)
                                
                            df_loc_year=df_loc_year.reset_index()
                            df_loc_year.to_feather(path_res)
                                
                            for PI in PIS:
                                pi_res_name=fr'{PI}_{EXP}.feather'
                                pi_res_folder=os.path.join(cfg.post_process_folder, EXP, 'PI', PI)
                                pi_path_res=os.path.join(pi_res_folder, pi_res_name)
                                
                                PI_module_name=f'CFG_{PI}'
                                unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{PI_module_name}')
                                print(unique_PI_CFG.name)
                                
                                if loc in unique_PI_CFG.locs_for_GLRRM:
                                    df_pi=unique_PI_CFG.GLRRM_1D_equations (df_loc_year)
                                    if not os.path.exists(pi_res_folder):
                                        os.makedirs(pi_res_folder)

                                    df_pi=df_pi.reset_index()
                                    df_pi.to_feather(pi_path_res)
                                else:
                                    print(f'not relevant to create 1D PI res for location {loc}')

                else:
                    print('selected agg_space is not available yet')
                    
        #con.close()
    def GLRMM_to_ISEE_1D_PI(self,  EXP, AGG_TIME, stats, PIS):
        path=os.path.join(cfg.GLRRM_RES, EXP, 'outputs')
        for PI in PIS:
            print(PI)
            PI_module_name=f'CFG_{PI}'
            unique_PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{PI_module_name}')
            sections= unique_PI_CFG.available_sections
            
            for time in AGG_TIME:
            
                if time=='YEAR':
    
                    for sect in sections:
                        
                        print(sect)
                        
                        station=unique_PI_CFG.dct_station_section[sect]
                        df=pd.read_csv(os.path.join(path, f'{station}_{unique_PI_CFG.GLRRM_name}_{unique_PI_CFG.GLRRM_units}_qm48_na_na.csv'), skiprows=cfg.header_lenght)
                        count=0
                        years=df['year'].unique()
                        d={'YEAR':years}
                        df_all=pd.DataFrame(data=d)
                        
                        for s in stats:
                            df=df[['year','values']]
                            count+=1
                            if s =='mean':
                                df_grouped=df.groupby(['year'], as_index=False).mean()
                                df_all[f'VAR{count}_sum']=df_grouped['values'].round(2)
                            elif s == 'max':
                                df_grouped=df.groupby(['year'], as_index=False).min()
                                df_all[f'VAR{count}_sum']=df_grouped['values'].round(2)
                            elif s=='min':
                                df_grouped=df.groupby(['year'], as_index=False).max()
                                df_all[f'VAR{count}_sum']=df_grouped['values'].round(2)
                            else:
                                print('stat in input is unavailable')
                        
                        print(df_all.head())
                        
                        res_dir=os.path.join(self.POST_PROCESS_ISEE, PI, time, 'SECTION', EXP, sect)
                        
                        if not os.path.exists(res_dir):
                            os.makedirs(res_dir) 
                        
                        df_all.to_feather(os.path.join(res_dir, f'{PI}_{time}_{EXP}_{sect}_{np.min(unique_PI_CFG.available_years)}_{np.max(unique_PI_CFG.available_years)}.feather'))
                        
                else:
                    print(f'AGG_TIME {AGG_TIME} id not available yet')       
                    quit()
                
            #df=pd.read_csv(path)
            

exps=POST_PROCESS_exp(cfg.GLRRM_RES, cfg.post_process_folder, ISEE_cfg.POST_PROCESS_RES, cfg.sep) 
experiments=exps.list_exps()

for EXP in experiments:
    print(EXP)
    
    exps.GLRMM_to_ISEE_1D_PI(EXP, ['YEAR'], ['min', 'mean', 'max'], ['WLVL_1D'])
    
    #===========================================================================
    # if cfg.overwrite_exp:
    #     exps.AGG_SPACE(EXP, ['YEAR', 'QM'], ['LOCATION'], ['mean', 'max', 'min'], ['MUSK_1D'])
    # else:
    #     path_exp=os.path.join(cfg.post_process_folder, EXP)
    #     if not os.path.exists(path_exp):
    #         exps.AGG_SPACE(EXP, ['YEAR', 'QM'], ['LOCATION'], ['mean', 'max', 'min'], ['MUSK_1D'])
    #     else:
    #         print(f'Experience: {EXP} already POST PROCESSED, skipping...')
    #===========================================================================
quit()








