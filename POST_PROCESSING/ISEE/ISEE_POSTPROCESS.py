import os
import pandas as pd
import importlib
import CFG_POST_PROCESS_ISEE as cfg
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import sysconfig
import os

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Environment path:", sys.prefix)
print("Installed site-packages:", sysconfig.get_paths()["purelib"])
print("Environment variables (conda/venv):", os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX"))


class POST_PROCESS_2D_tiled:

    def __init__(self, pis, ISEE_RES, POST_PROCESS_RES, sep):
        self.pis=pis
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep

    def agg_YEAR(self, folder_space, y, columns):
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        liste_df=[]
        liste_file_year=[f for f in liste_files if str(y) in f.split('_')[-1]]

        if len(liste_file_year) >0:
            for feather in liste_file_year:
                df_temp=pd.read_feather(feather)
                liste_df.append(df_temp)
            # print('concatenating....')
            df_year=pd.concat(liste_df, ignore_index=True)
            no_dat_year = 99999
        else:
            df_year=pd.DataFrame(0, index=range(1), columns=columns)
            no_dat_year=y
        return df_year, no_dat_year

    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, agg_year_param, path_feather_year, years_list, space):
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)

        df_space[AGG_TIME]=years_list

        if AGG_SPACE == 'TILE':
            df_space['TILE']=space

        if not os.path.exists(path_res):
            os.makedirs(path_res)
        for y in years_list:
            if AGG_SPACE == 'PLAN' or AGG_SPACE == 'SECTION':
                df_year, no_dat_year=self.agg_YEAR(agg_year_param, y, columns)
            elif AGG_SPACE == 'TILE':
                path_feather_year2=path_feather_year.replace('foo', str(y))
                if not os.path.exists(path_feather_year2):
                    continue
                df_year=pd.read_feather(path_feather_year2)
                no_dat_year=99999
            if y == no_dat_year:
                continue
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

    def AGG_PT_ID_ALL_YEARS(self, PI, p, s, var, path_res, AGG_TIME, PI_CFG, years_list):
        count_y=0
        tiles=cfg.dct_tile_sect[s]

        for t in tiles:
            count_y=0

            res_name = os.path.join(path_res,
                                    f'{var}_{PI}_{AGG_TIME}_{p}_{s}_PT_ID_{t}_{min(years_list)}_{max(years_list)}')

            if os.path.exists(res_name):
                print(fr'AGG level of PT_ID for plan {p} and section {s} and tile {t} already exists {PI}.... skipping!')
                continue

            for y in years_list:

                feather=os.path.join(self.ISEE_RES, PI,p, s, str(y), f'{PI}_{p}_{s}_{t}_{y}.feather')

                if not os.path.exists(feather):
                    print('dont exists skipping...')
                    continue
                else:
                    count_y += 1
                    df_temp=pd.read_feather(feather)
                    df_temp[str(y)]=df_temp[var]

                    if 'XVAL' in list(df_temp):
                        df_temp['LON']=df_temp['XVAL']
                        df_temp['LAT'] = df_temp['YVAL']
                        df_temp = df_temp[[PI_CFG.id_column_name, str(y), 'LAT', 'LON']]

                    elif 'LAT' in list(df_temp):
                        df_temp = df_temp[[PI_CFG.id_column_name, str(y), 'LAT', 'LON']]

                    else:
                        # print('fetching lat lon info from isee-tiles...', PI)
                        t=feather.split('_')[-2]
                        df_t=pd.read_feather(fr"{self.ISEE_RES}\Tiles\GLAM_DEM_ISEE_TILE_{t}.feather")
                        df_t=df_t[['PT_ID', 'LAT', 'LON']]
                        df_temp=df_temp[[PI_CFG.id_column_name, str(y)]]
                        df_temp=df_temp.merge(df_t, on=PI_CFG.id_column_name, how='left', suffixes=('', ''))
                    if count_y==1:
                        df_main=df_temp
                    elif count_y==0:
                        continue
                    else:
                        df_main = df_main.merge(df_temp, on=[PI_CFG.id_column_name, 'LAT', 'LON'], how='outer',suffixes=('', ''))

            if count_y==0:
                continue
            else:
                print(df_main.head())
            res_name=os.path.join(path_res, f'{var}_{PI}_{AGG_TIME}_{p}_{s}_PT_ID_{t}_{min(years_list)}_{max(years_list)}')
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
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)

                if AGG_TIME=='YEAR':
                    if AGG_SPACE=='PLAN':
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            print(space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)

                            if os.path.exists(path_res):
                                print(f'AGG level of {AGG_SPACE} for plan {space} already exists skipping....')
                                continue

                            if space in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(years_list)}_{max(years_list)}.feather'

                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, agg_year_param ,'', years_list,space)

                    elif AGG_SPACE=='SECTION':
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            for space in PI_CFG.available_sections:
                                print(space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)

                                if os.path.exists(path_res):
                                    print(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue

                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.feather'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p, space)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, agg_year_param, '', years_list, space)

                    elif AGG_SPACE=='TILE':
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if p in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            for s in PI_CFG.available_sections:
                                for space in cfg.dct_tile_sect[s]:
                                    print(space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    if os.path.exists(path_res):
                                        print(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        continue
                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(years_list)}_{max(years_list)}.feather'
                                    path_feather_year=os.path.join(self.ISEE_RES, PI, p, s, 'foo' , f'{PI}_{p}_{s}_{space}_foo.feather')
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, '', path_feather_year, years_list, space)

                    elif AGG_SPACE=='PT_ID':
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if p in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            for s in PI_CFG.available_sections:
                                path_sect=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                if os.path.exists (path_sect):
                                    print(fr'post_processed results for {PI}, {p}, {s} already exists... skipping... but carefull check if all the tiles and variables where processed, if not delete de folder and run again')
                                    continue

                                for var in list(PI_CFG.dct_var.keys()):
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                    if not os.path.exists(path_res):
                                        os.makedirs(path_res)
                                    res_name=f'{var}_{PI}_{AGG_TIME}_{p}_{s}_{AGG_SPACE}_{min(years_list)}_{max(years_list)}.feather'

                                    path_check=os.path.join(path_res, res_name)
                                    if os.path.exists(path_check):
                                        print(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {s} and var {var} already exists skipping....')
                                        continue

                                    self.AGG_PT_ID_ALL_YEARS(PI, p, s, var, path_res, AGG_TIME, PI_CFG, years_list)

                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()
                elif AGG_TIME=='QM':
                    ### NOT coded yet!!
                    pass
                else:
                    pass

class POST_PROCESS_2D_not_tiled:

    def __init__(self, pis, ISEE_RES, POST_PROCESS_RES, sep):

        self.pis=pis
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep

    def agg_YEAR(self, folder_space, y):
        print(folder_space)
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        liste_df=[]
        liste_file_year=[f for f in liste_files if f'{str(y)}.feather' in f]

        # print(y, len(liste_file_year))

        if len(liste_file_year)!=0:
            for feather in liste_file_year:
                df_temp=pd.read_feather(feather)
                liste_df.append(df_temp)
            df_year=pd.concat(liste_df, ignore_index=True)

            empty_year=False
        else:
            df_year=[]
            empty_year=True

        return df_year, empty_year

    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG, years_list):
        print('AGG_SPACE_YEAR')
        not_empty=False
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        df_space[AGG_TIME]=years_list

        if AGG_SPACE == 'TILE':
            df_space['TILE']=space

        if not os.path.exists(path_res):
            os.makedirs(path_res)
        for y in years_list:
            if AGG_SPACE == 'PLAN':
                df_year, empty_year=self.agg_YEAR(agg_year_param, y)
                if empty_year:
                    print(y, 'EMPTY!!!')
                    continue

            elif AGG_SPACE == 'SECTION':
                df_year, empty_year=self.agg_YEAR(agg_year_param, y)
                df_year=df_year.loc[df_year['SECTION']==space]
                if empty_year:
                    print(y, 'EMPTY!!!')
                    continue

            elif AGG_SPACE == 'TILE':
                df_year, empty_year=self.agg_YEAR(agg_year_param, y)
                if empty_year:
                    print(y, 'EMPTY!!!')
                    continue
                df_year=df_year.loc[df_year['TILE']==int(space)]

            for var in list_var:
                stats=PI_CFG.var_agg_stat[var]
                for stat in stats:
                    if stat=='sum':
                        value=df_year[var].sum()
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=value
                        not_empty=True
                    elif stat=='mean':
                        value = df_year[var].mean()
                        df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=value
                        not_empty=True
                    else:
                        print('STAT value provided is unavailable')

        if not_empty:
            df_space=df_space.reset_index()
            df_space.to_feather(os.path.join(path_res, res_name))
        else:
            print(f'no data for this space: {space}, nothing to write...')

    def AGG_PT_ID_ALL_YEARS(self, PI, p, var, path_res, AGG_TIME, PI_CFG, s, years_list):

        tiles = cfg.dct_tile_sect[s]
        for t in tiles:
            count_y = 0


            res_name = os.path.join(path_res,
                                    f'{var}_{PI}_{AGG_TIME}_{p}_{s}_PT_ID_{t}_{min(years_list)}_{max(years_list)}')

            if os.path.exists(res_name):
                print(fr'AGG level of PT_ID for plan {p} and section {s} and tile {t} already exists {PI}.... skipping!')
                continue

            for y in years_list:
                feather = os.path.join(self.ISEE_RES, PI, p, f'{PI}_{p}_{y}.feather')
                if not os.path.exists(feather):
                    continue
                else:
                    # print(fr'processing... plan {p} and section {s} and tile {t} for year {y}')
                    count_y += 1
                    df_temp=pd.read_feather(feather)
                    df_temp=df_temp.loc[df_temp['SECTION']==s]
                    df_temp = df_temp.loc[df_temp['TILE'] == t]
                    df_temp=df_temp.drop_duplicates(subset=['PT_ID'])
                    if len(df_temp)==0:
                        count_y -= 1
                        continue

                    df_temp[str(y)] = df_temp[var]

                    if 'XVAL' in list(df_temp):
                        df_temp['LON'] = df_temp['XVAL']
                        df_temp['LAT'] = df_temp['YVAL']
                        df_temp = df_temp[[PI_CFG.id_column_name, str(y), 'LAT', 'LON']]

                    elif 'LAT' in list(df_temp):
                        df_temp = df_temp[[PI_CFG.id_column_name, str(y), 'LAT', 'LON']]

                    else:
                        # print('fetching lat lon info from isee-tiles...', PI)
                        df_t = pd.read_feather(fr"{self.ISEE_RES}\Tiles\GLAM_DEM_ISEE_TILE_{t}.feather")
                        df_t['TILE']=int(t)
                        df_t = df_t[['PT_ID', 'LAT', 'LON']]
                        df_temp = df_temp[[PI_CFG.id_column_name, str(y)]]
                        df_temp = df_temp.merge(df_t, on=PI_CFG.id_column_name, how='left', suffixes=('', ''))
                    if count_y == 1:
                        df_main = df_temp
                    elif count_y == 0:
                        continue
                    else:
                        df_main = df_main.merge(df_temp, on=[PI_CFG.id_column_name, 'LAT', 'LON'], how='outer',
                                                suffixes=('', ''))
            if count_y == 0:
                continue
            else:
                print(df_main.head())

            res_name = os.path.join(path_res,
                                    f'{var}_{PI}_{AGG_TIME}_{p}_{s}_PT_ID_{t}_{min(years_list)}_{max(years_list)}.feather')
            df_main.to_feather(res_name)

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
                list_var=list(PI_CFG.dct_var.keys())
                stats=[]
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)
                if AGG_TIME=='YEAR':
                    if AGG_SPACE=='PLAN':
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if space in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            print(space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)

                            if os.path.exists(path_res):
                                print(
                                    f'AGG level of {AGG_SPACE} for plan {space}  already exists skipping....')
                                continue

                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(years_list)}_{max(years_list)}.feather'
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG, years_list)

                    elif AGG_SPACE=='SECTION':
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            for space in PI_CFG.available_sections:
                                print(p, space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.feather'

                                if os.path.exists(path_res):
                                    print(
                                        f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue

                                agg_year_param=os.path.join(self.ISEE_RES, PI, p)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG, years_list)

                    elif AGG_SPACE=='TILE':
                        columns.append('TILE')
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            for s in PI_CFG.available_sections:
                                for space in cfg.dct_tile_sect[s]:
                                    print(p, s, space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)

                                    if os.path.exists(path_res):
                                        print(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        continue

                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(years_list)}_{max(years_list)}.feather'
                                    agg_year_param=os.path.join(self.ISEE_RES, PI, p)
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG, years_list)

                    elif AGG_SPACE=='PT_ID':
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if p in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            for s in PI_CFG.available_sections:
                                path_sect=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                if os.path.exists (path_sect):
                                    print(fr'post_processed results for {PI}, {p}, {s} already exists... skipping... but carefull check if all the iles and variables where processed, if not delete de folder and run again')
                                    continue
                                for var in list(PI_CFG.dct_var.keys()):
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                    if not os.path.exists(path_res):
                                        os.makedirs(path_res)

                                    # deja la condition pour voir si ca existe dans cette fonction
                                    self.AGG_PT_ID_ALL_YEARS(PI, p, var, path_res, AGG_TIME, PI_CFG, s, years_list)

                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()

                elif AGG_TIME=='QM':
                    ### NOT coded yet!!
                    pass

                else:
                    pass

class POST_PROCESS_1D:

    def __init__(self, pis,ISEE_RES, POST_PROCESS_RES, sep):

        self.pis=pis
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep

    def agg_YEAR(self, folder_space):
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        df_year=pd.DataFrame()
        liste_df=[]
        if len(liste_files) != 0:
            exists=True
            for feather in liste_files:
                if feather.split('.')[-1]=='feather':
                    df_temp=pd.read_feather(feather)
                    liste_df.append(df_temp)
            df_year = pd.concat(liste_df, ignore_index=True)
        else:
            df_year=0
            exists = False
        return df_year, exists

    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG, years_list):
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        df_space[AGG_TIME]=years_list
        if not os.path.exists(path_res):
            os.makedirs(path_res)
        if AGG_SPACE == 'PLAN':
            df_year, exists=self.agg_YEAR(agg_year_param)
            if exists:
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
            df_space, exists=self.agg_YEAR(agg_year_param)

            if exists:
                columns=['YEAR']
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for stat in stats:
                        var_stat=var+f'_{stat}'
                        df_space[var_stat]=df_space[var]
                        columns.append(var_stat)
                df_space=df_space[columns]

        if exists:
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
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if space in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            print(space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)

                            if os.path.exists(path_res):
                                print(
                                    f'AGG level of {AGG_SPACE} for plan {space} already exists skipping...')
                                continue

                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(years_list)}_{max(years_list)}.feather'
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG, years_list)

                    elif AGG_SPACE=='SECTION':
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:

                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            for space in PI_CFG.available_sections:
                                print(p, space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)

                                if os.path.exists(path_res):
                                    print(
                                        f'AGG level of {AGG_SPACE} for plan {p} in section {space} already exists skipping...')
                                    continue

                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.feather'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p, space)
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG, years_list)

                    else:
                        print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                        quit()

                elif AGG_TIME=='QM':
                    ### NOT coded yet!!
                    pass

                else:
                    pass


tiled=POST_PROCESS_2D_tiled(cfg.pis_2D_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

not_tiled=POST_PROCESS_2D_not_tiled(cfg.pis_2D_not_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

pi_1D=POST_PROCESS_1D(cfg.pis_1D, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

# for pi in not_tiled.pis:
#     print(pi)
#     not_tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'])
#     # not_tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION'])

# for pi in tiled.pis:
#     print(pi)
#     tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'])
#     # tiled.agg_2D_space(pi, ['YEAR'], ['PLAN'])
#     # tiled.agg_2D_space(pi, ['YEAR'], ['SECTION'])


for pi in pi_1D.pis:
    print(pi)
    pi_1D.agg_1D_space(pi, ['YEAR'], ['PLAN', 'SECTION'])

quit()



