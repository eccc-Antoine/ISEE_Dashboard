import os
import pandas as pd
import importlib
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
import CFG_POST_PROCESS_ISEE as cfg
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
import sysconfig
import os
print(cfg)
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Environment path:", sys.prefix)
print("Installed site-packages:", sysconfig.get_paths()["purelib"])
print("Environment variables (conda/venv):", os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX"))


class POST_PROCESS_2D_tiled:

    def find_pt_id(self, df):
        df2 = df.drop(columns='PT_ID')
        overall_mean = df2.to_numpy().mean()
        abs_diff = (df2 - overall_mean).abs()
        min_diff = abs_diff.min().min()
        closest_locs = list(zip(*((abs_diff == min_diff).to_numpy().nonzero())))
        closest_positions = [(df2.index[r], df2.columns[c]) for r, c in closest_locs]
        print(closest_positions)
        closest_positions = closest_positions[0]
        id = df['PT_ID'].loc[closest_positions[0]]
        id=int(id)
        return id

    def __init__(self, pis, ISEE_RES, POST_PROCESS_RES, sep, logger=None):
        self.pis=pis
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        self.logger=logger

    # Lire les résultats de l'année y
    def agg_YEAR(self, folder_space, y, columns):
        # Exécuter pour une année (y)
        # Lister tous les fichiers avec les résultats pour l'année y
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        liste_df=[]
        liste_file_year=[f for f in liste_files if str(y) in f.split('_')[-1]]

        # S'il y a des fichiers pour l'année y, les lire et les concatener
        if len(liste_file_year) >0:
            for feather in liste_file_year:
                df_temp=pd.read_feather(feather)
                liste_df.append(df_temp)
            # print('concatenating....')
            # Concatenate all years
            df_year=pd.concat(liste_df, ignore_index=True)
            no_dat_year = 99999
        # Si pas de fichier, il n'y a pas de données pour cette année
        else:
            df_year=pd.DataFrame(0, index=range(1), columns=columns)
            no_dat_year=y
        return df_year, no_dat_year

    # Aggréger les résultats par année
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, agg_year_param, path_feather_year, years_list, space, PI):
        # df_space sera le fichier final
        # Créer la colonne YEAR (ou QM quand ce sera implémenté)
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        df_space[AGG_TIME]=years_list

        # Ajouter la colonne 'TILE'
        if AGG_SPACE == 'TILE':
            df_space['TILE']=space

        if not os.path.exists(path_res):
            os.makedirs(path_res)
        count_id=0
        # Pour chaque année, aggréger les résultats (par plan, section, tuile ou pt_id)
        for y in years_list:
            # print(y)
            count_id+=1
            if AGG_SPACE == 'PLAN' or AGG_SPACE == 'SECTION':
                # print('ok')
                df_year, no_dat_year=self.agg_YEAR(agg_year_param, y, columns)
            elif AGG_SPACE == 'TILE':
                # Nom du fichier de l'année courante
                path_feather_year2=path_feather_year.replace('foo', str(y))
                if not os.path.exists(path_feather_year2):
                    continue
                # Lire le fichier
                df_year=pd.read_feather(path_feather_year2)
                no_dat_year=99999
            # print('no_dat_year=',  no_dat_year)
            # Si pas de donnée, skip
            if y == no_dat_year:
                continue

            # Pour toutes les variables
            for var in list_var:
                # Pour toutes les stats
                for stat in stats:
                    ## ne pas faire la moyenne des points pour les niveaux d'eau mais plutôt utiliser un pt_id qui a une valeur proche de la moyenne
                    if PI=='WL_ISEE_2D' and AGG_SPACE == 'TILE':
                        if count_id==1:
                            if self.logger:
                                self.logger.info('determine which pt_id to select to represent the tile')
                            else:
                                print('determine which pt_id to select to represent the tile')
                            id=self.find_pt_id(df_year)
                            # print(id)
                            # print(list(df_year))
                            # print(var)

                            # print(df_year.loc[df_year['PT_ID'] == id, var].iloc[0])
                        mask = df_space[AGG_TIME] == y
                        #print(mask)
                        #print(len(mask))
                        # print(id)
                        id=int(id)
                        val = df_year.loc[df_year['PT_ID']== id]
                        # print(val)
                        # print(var)
                        #value = df_year.loc[df_year['PT_ID'] == id, var].iloc[0]

                        try:
                            #value = df_year.loc[df_year['PT_ID'] == id, var].head(1).item()
                            value = df_year.loc[df_year['PT_ID'] == id, var].iloc[0]

                        except Exception as e:
                            # Extract the problematic subset (for debugging)
                            subset = df_year.loc[df_year['PT_ID'] == id]

                            # print(subset)
                            # print(list(subset))
                            # print(subset.info())

                            # Write to CSV
                            debug_path = fr"P:\GLAM\Dashboard\prod\debug_PTID_{id}_{var}.csv"
                            subset.to_csv(debug_path, index=False, sep=';')

                            if self.logger:
                                self.logger.error(f"ERROR retrieving value for PT_ID={id}, var={var}. Filtered dataframe saved as: {debug_path}")
                                self.logger.error(f"Filtered dataframe was:\n{subset}")
                            else:
                                print(f"\nERROR retrieving value for PT_ID={id}, var={var}")
                                print(f"Filtered dataframe saved as: {debug_path}\n")
                                print("Filtered dataframe was:")
                                print(subset)

                            if len(subset) != 1:
                                print('got ya!', len(subset))

                            # Optional: re-raise the original error
                            raise e
                        # print(f'{value}..')
                        df_space.loc[mask, f'{var}_{stat}'] = value
                        #df_space.loc[df_space[AGG_TIME] == y, f'{var}_{stat}'] = df_year.loc[df_year['PT_ID']==id, var].iloc[0]

                    # Calculer la statistique pour la variable pour l'année courante
                    else:
                        if stat=='sum':
                            df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].sum()
                        elif stat=='mean':
                            df_space.loc[df_space[AGG_TIME]==y, f'{var}_{stat}']=df_year[var].mean()
                        else:
                            if self.logger:
                                self.logger.error('STAT value provided is unavailable')
                            else:
                                print('STAT value provided is unavailable')
        df_space=df_space.reset_index()
        # Sauvegarder en parquet avec 6 décimales
        df_space = pd.concat([df_space[['index','YEAR']],df_space.drop(columns=['index','YEAR']).round(6)],axis=1)
        df_space.to_parquet(os.path.join(path_res, res_name), engine="pyarrow", index=False, compression="snappy")

    def AGG_PT_ID_ALL_YEARS(self, PI, p, s, var, path_res, AGG_TIME, PI_CFG, years_list):
        count_y=0
        tiles=cfg.dct_tile_sect[s]
        # Pour toutes les tuiles et toutes les années, aggréger par pt_id
        for t in tiles:
            count_y=0
            res_name=os.path.join(path_res, f'{var}_{PI}_{AGG_TIME}_{p}_{s}_PT_ID_{t}_{min(years_list)}_{max(years_list)}.parquet')
            if os.path.exists(res_name):
                if self.logger:
                    self.logger.info(fr'AGG level of PT_ID for plan {p} and section {s} and tile {t} already exists {PI}.... skipping!')
                else:
                    print(fr'AGG level of PT_ID for plan {p} and section {s} and tile {t} already exists {PI}.... skipping!')
                continue

            for y in years_list:

                feather=os.path.join(self.ISEE_RES, PI,p, s, str(y), f'{PI}_{p}_{s}_{t}_{y}.feather')
                # skip si pas de données cette année-là
                if not os.path.exists(feather):
                    if self.logger:
                        self.logger.info(f'File for year {y} for tile {t} does not exists skipping...')
                    else:
                        print('dont exists skipping...')
                    continue
                # Ajouter latitude/longitude au besoin et garder que lat, lon et pt_id
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

                    # Ajouter les résultats au gros dataframe (df_main)
                    if count_y==1:
                        df_main=df_temp
                    elif count_y==0:
                        continue
                    else:
                        df_main = df_main.merge(df_temp, on=[PI_CFG.id_column_name, 'LAT', 'LON'], how='outer',suffixes=('', ''))

            if count_y==0:
                continue
            else:
                if self.logger:
                    self.logger.info(df_main.head())
                else:
                    print(df_main.head())
            # sauvegarer le fichier final avec 6 décimales
            df_main = pd.concat([df_main[['PT_ID','LAT','LON']],df_main.drop(columns=['PT_ID','LAT','LON']).round(6)],axis=1)
            df_main.to_parquet(res_name, engine="pyarrow", index=False, compression="snappy")

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        '''
        PI = PI accronym (ex. Northern Pike = PIKE_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION', 'TILE']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean']
        '''
        # This is the main function that calls all the other ones
        pi_module_name=f'CFG_{PI}'
        PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        # Pour toutes les aggrégations temporelles (seulement YEAR pour l'instant)
        for AGG_TIME in AGGS_TIME:
            # Pour tous les espaces d'aggrégation (PLAN, SECTION, TILE, PT_ID)
            for AGG_SPACE in AGGS_SPACE:
                if self.logger:
                    self.logger.info('  ->' + AGG_SPACE)
                print('  ->',AGG_SPACE)
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)

                # Aggrégation
                if AGG_TIME=='YEAR':
                    # PLAN
                    if AGG_SPACE=='PLAN':
                        # Pour tous les plans dans les config du PI
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            if self.logger:
                                self.logger.info('    -->' + space)
                            print('    -->',space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            # Si les résultats existent déjà, skipper
                            if os.path.exists(path_res):
                                if self.logger:
                                    self.logger.info(f'AGG level of {AGG_SPACE} for plan {space} already exists skipping....')
                                else:
                                    print(f'AGG level of {AGG_SPACE} for plan {space} already exists skipping....')
                                continue
                            # Extraire la liste des années
                            if space in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Nom du fichier final
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(years_list)}_{max(years_list)}.parquet'

                            agg_year_param=os.path.join(self.ISEE_RES, PI, space) # ici space est un plan
                            # Aggréger les résulats par plan et par année
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, agg_year_param ,'', years_list,space, PI)
                    # SECTION
                    elif AGG_SPACE=='SECTION':
                        # Pour tous les plans dans les config du PI
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections, aggréger pour le plan courant
                            for space in PI_CFG.available_sections:
                                if self.logger:
                                    self.logger.info('    -->' + space)
                                print('    -->',space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                # Si les résultats existent déjà, skipper
                                if os.path.exists(path_res):
                                    if self.logger:
                                        self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    else:
                                        print(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue

                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                agg_year_param=os.path.join(self.ISEE_RES, PI, p, space) # space ici est une section et p est un plan (l'agg)
                                # Aggréger les résulats par plan et par année
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, agg_year_param, '', years_list, space, PI)
                    # TILE
                    elif AGG_SPACE=='TILE':
                        # Pour tous les plans dans les config du PI
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections
                            for s in PI_CFG.available_sections:
                                # Pour toutes les tuiles, aggréger pour le plan courant
                                for space in cfg.dct_tile_sect[s]:
                                    if self.logger:
                                        self.logger.info('    -->' + space)
                                    print('    -->',space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    # Skip si les résultats existent déjà
                                    if os.path.exists(path_res):
                                        if self.logger:
                                            self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        else:
                                            print(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        continue
                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                    path_feather_year=os.path.join(self.ISEE_RES, PI, p, s, 'foo' , f'{PI}_{p}_{s}_{space}_foo.feather')
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, list_var, stats, '', path_feather_year, years_list, space, PI)
                    # PT_ID
                    elif AGG_SPACE=='PT_ID':
                        # Pour tous les plans dans les config du PI
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections disponibles
                            for s in PI_CFG.available_sections:
                                path_sect=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                # Skip si le résultat existe déjà
                                if os.path.exists (path_sect):
                                    if self.logger:
                                        self.logger.info(fr'post_processed results for {PI}, {p}, {s} already exists... skipping... but carefull check if all the tiles and variables where processed, if not delete de folder and run again')
                                    else:
                                        print(fr'post_processed results for {PI}, {p}, {s} already exists... skipping... but carefull check if all the tiles and variables where processed, if not delete de folder and run again')
                                    continue
                                # Pour toutes les variables du PI, aggréger par PT ID
                                for var in list(PI_CFG.dct_var.keys()):
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                    if not os.path.exists(path_res):
                                        os.makedirs(path_res)
                                    res_name=f'{var}_{PI}_{AGG_TIME}_{p}_{s}_{AGG_SPACE}_{min(years_list)}_{max(years_list)}.parquet'

                                    path_check=os.path.join(path_res, res_name)
                                    if os.path.exists(path_check):
                                        if self.logger:
                                            self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and var {var} already exists skipping....')
                                        else:
                                            print(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and var {var} already exists skipping....')
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

    def __init__(self, pis, ISEE_RES, POST_PROCESS_RES, sep, logger=None):

        self.pis=pis
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        self.logger=logger

    # Lire les résultats de l'année y
    def agg_YEAR(self, folder_space, y):
        # Exécuter pour une année (y)
        # Lister tous les fichiers avec les résultats pour l'année y
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        liste_df=[]
        liste_file_year=[f for f in liste_files if f'{str(y)}.feather' in f]

        # print(y, len(liste_file_year))
        # S'il y a des fichiers pour l'année y, les lire et les concatener
        if len(liste_file_year)!=0:
            for feather in liste_file_year:
                df_temp=pd.read_feather(feather)
                liste_df.append(df_temp)
            # Concatenate all years
            df_year=pd.concat(liste_df, ignore_index=True)
            empty_year=False
        else:
            df_year=[]
            empty_year=True

        return df_year, empty_year

    # Aggréger les résultats par année
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG, years_list):
        # print('AGG_SPACE_YEAR')
        # df_space sera le fichier final
        # Créer la colonne YEAR (ou QM quand ce sera implémenté)
        not_empty=False
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        df_space[AGG_TIME]=years_list

        # Ajouter la colonne 'TILE'
        if AGG_SPACE == 'TILE':
            df_space['TILE']=space

        if not os.path.exists(path_res):
            os.makedirs(path_res)
        # Pour chaque année, aggréger les résultats (par plan, section, tuile ou pt_id)
        for y in years_list:
            if AGG_SPACE == 'PLAN':
                df_year, empty_year=self.agg_YEAR(agg_year_param, y)
                if empty_year:
                    if self.logger:
                        self.logger.info(f'Year {y} is empty')
                    else:
                        print(y, 'EMPTY!!!')
                    continue

            elif AGG_SPACE == 'SECTION':
                df_year, empty_year=self.agg_YEAR(agg_year_param, y)
                df_year=df_year.loc[df_year['SECTION']==space]
                if empty_year:
                    if self.logger:
                        self.logger.info(f'Year {y} is empty')
                    else:
                        print(y, 'EMPTY!!!')
                    continue

            elif AGG_SPACE == 'TILE':
                # Nom du fichier de l'année courante
                df_year, empty_year=self.agg_YEAR(agg_year_param, y)
                if empty_year:
                    if self.logger:
                        self.logger.info(f'Year {y} is empty')
                    else:
                        print(y, 'EMPTY!!!')
                    continue
                # Lire le fichier
                df_year=df_year.loc[df_year['TILE']==int(space)]

            # Pour toutes les variables
            for var in list_var:
                stats=PI_CFG.var_agg_stat[var]
                # Pour toutes les stats, calculer la statistique pour la variable pour l'année courante
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
                        if self.logger:
                            self.logger.error('STAT value provided is unavailable')
                        else:
                            print('STAT value provided is unavailable')
        # Sauvegarder en parquet
        if not_empty:
            df_space=df_space.reset_index()
            df_space = pd.concat([df_space[['index','YEAR']],df_space.drop(columns=['index','YEAR']).round(6)],axis=1)
            df_space.to_parquet(os.path.join(path_res, res_name))
        else:
            if self.logger:
                self.logger.info(f'no data for this space: {space}, nothing to write...')
            else:
                print(f'no data for this space: {space}, nothing to write...')

    def AGG_PT_ID_ALL_YEARS(self, PI, p, var, path_res, AGG_TIME, PI_CFG, s, years_list):

        tiles = cfg.dct_tile_sect[s]
        # Pour toutes les tuiles et toutes les années, aggréger par pt_id
        for t in tiles:
            count_y = 0
            res_name = os.path.join(path_res,
                                    f'{var}_{PI}_{AGG_TIME}_{p}_{s}_PT_ID_{t}_{min(years_list)}_{max(years_list)}.parquet')
            if os.path.exists(res_name):
                if self.logger:
                    self.logger.info(fr'AGG level of PT_ID for plan {p} and section {s} and tile {t} already exists {PI}.... skipping!')
                else:
                    print(fr'AGG level of PT_ID for plan {p} and section {s} and tile {t} already exists {PI}.... skipping!')
                continue

            for y in years_list:
                feather = os.path.join(self.ISEE_RES, PI, p, f'{PI}_{p}_{y}.feather')
                # skip si pas de données cette année-là
                if not os.path.exists(feather):
                    continue
                # Ajouter latitude/longitude au besoin et garder que lat, lon et pt_id
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
                    # Ajouter les résultats au gros dataframe (df_main)
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
                if self.logger:
                    self.logger.info(df_main.head())
                else:
                    print(df_main.head())
            # sauvegarer le fichier final
            df_main = pd.concat([df_main[['PT_ID','LAT','LON']],df_main.drop(columns=['PT_ID','LAT','LON']).round(6)],axis=1)
            df_main.to_parquet(res_name, engine="pyarrow", index=False, compression="snappy")

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION', 'TILE']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean']
        '''
        # This is the main function that calls all the other ones
        pi_module_name=f'CFG_{PI}'
        PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        # Pour toutes les aggrégations temporelles (seulement YEAR pour l'instant)
        for AGG_TIME in AGGS_TIME:
            # Pour tous les espaces d'aggrégation (PLAN, SECTION, TILE, PT_ID)
            for AGG_SPACE in AGGS_SPACE:
                if self.logger:
                    self.logger.info('  ->' + AGG_SPACE)
                print('  ->',AGG_SPACE)
                list_var=list(PI_CFG.dct_var.keys())
                stats=[]
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)

                # Aggrégation
                if AGG_TIME=='YEAR':
                    # PLAN
                    if AGG_SPACE=='PLAN':
                        # Pour tous les plans dans les config du PI
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if space in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            if self.logger:
                                self.logger.info('    -->' + space)
                            print('    -->',space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            # Si les résultats existent déjà, skipper
                            if os.path.exists(path_res):
                                if self.logger:
                                    self.logger.info(f'AGG level of {AGG_SPACE} for plan {space} already exists skipping....')
                                else:
                                    print(f'AGG level of {AGG_SPACE} for plan {space}  already exists skipping....')
                                continue
                            # Nom du fichier final
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG, years_list)
                    # SECTION
                    elif AGG_SPACE=='SECTION':
                        # Pour tous les plans dans les config du PI
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections, aggréger pour le plan courant
                            for space in PI_CFG.available_sections:
                                if self.logger:
                                    self.logger.info('    -->' + p + ' ' + space)
                                print('    -->',p, space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                # Si les résultats existent déjà, skipper
                                if os.path.exists(path_res):
                                    if self.logger:
                                        self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    else:
                                        print(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue

                                agg_year_param=os.path.join(self.ISEE_RES, PI, p)
                                # Aggréger les résulats par plan et par année
                                self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG, years_list)
                    # TILE
                    elif AGG_SPACE=='TILE':
                        # Pour tous les plans dans les config du PI
                        columns.append('TILE')
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections
                            for s in PI_CFG.available_sections:
                                # Pour toutes les tuiles, aggréger pour le plan courant
                                for space in cfg.dct_tile_sect[s]:
                                    if self.logger:
                                        self.logger.info('    -->' + p + ' ' + s + ' ' + str(space))
                                    print('    -->',p, s, space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    # Skip si les résultats existent déjà
                                    if os.path.exists(path_res):
                                        if self.logger:
                                            self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        else:
                                            print(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        continue

                                    res_name=f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                    agg_year_param=os.path.join(self.ISEE_RES, PI, p)
                                    self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, '', PI_CFG, years_list)
                    # PT_ID
                    elif AGG_SPACE=='PT_ID':
                        # Pour tous les plans dans les config du PI
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list=PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections disponibles
                            for s in PI_CFG.available_sections:
                                path_sect=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s)
                                # Skip si le résultat existe déjà
                                if os.path.exists (path_sect):
                                    if self.logger:
                                        self.logger.info(fr'post_processed results for {PI}, {p}, {s} already exists... skipping... but carefull check if all the tiles and variables where processed, if not delete de folder and run again')
                                    else:
                                        print(fr'post_processed results for {PI}, {p}, {s} already exists... skipping... but carefull check if all the iles and variables where processed, if not delete de folder and run again')
                                    continue
                                # Pour toutes les variables du PI, aggréger par PT ID
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

    def __init__(self, pis,ISEE_RES, POST_PROCESS_RES, sep, logger=None):

        self.pis=pis
        self.ISEE_RES=ISEE_RES
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        self.logger=logger

    # Lire les résultats
    def agg_YEAR(self, folder_space):
        # Exécuter pour toute la période
        # Lister tous les fichiers avec les résultats
        liste_files=[]
        for root, dirs, files in os.walk(folder_space):
            for name in files:
                liste_files.append(os.path.join(root, name))
        df_year=pd.DataFrame()
        liste_df=[]
        # S'il y a des fichiers, les lire et les concatener
        if len(liste_files) != 0:
            exists=True
            for feather in liste_files:
                if feather.split('.')[-1]=='feather':
                    df_temp=pd.read_feather(feather)
                    liste_df.append(df_temp)
            # Concatenate all
            df_year = pd.concat(liste_df, ignore_index=True)
        else:
            df_year=0
            exists = False
        return df_year, exists

    # Aggréger les résultats par année
    def AGG_SPACE_YEAR(self, path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param, path_feather_year, PI_CFG, years_list):
        # df_space sera le fichier final
        # Créer la colonne YEAR (ou QM quand ce sera implémenté)
        dct_df_space=dict.fromkeys(tuple(columns),[])
        df_space=pd.DataFrame(dct_df_space)
        df_space[AGG_TIME]=years_list

        if not os.path.exists(path_res):
            os.makedirs(path_res)
        # aggréger les résultats (par plan, section)
        if AGG_SPACE == 'PLAN':
            df_year, exists=self.agg_YEAR(agg_year_param)
            # Pour toutes les stats, calculer la statistique
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
                    if self.logger:
                        self.logger.error('STAT value provided is unavailable')
                    else:
                        print('STAT value provided is unavailable')

        elif AGG_SPACE == 'SECTION':
            df_space, exists=self.agg_YEAR(agg_year_param)

            if exists:
                columns=['YEAR']
                # Pour toutes les stats et variables, calculer la statistique
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for stat in stats:
                        var_stat=var+f'_{stat}'
                        df_space[var_stat]=df_space[var]
                        columns.append(var_stat)
                df_space=df_space[columns]
        # Sauvegarder en parquet
        if exists:
            df_space=df_space.reset_index()
            df_space = pd.concat([df_space[['index','YEAR']],df_space.drop(columns=['index','YEAR']).round(6)],axis=1)
            df_space.to_parquet(os.path.join(path_res, res_name))

    def agg_1D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean']
        '''
        # This is the main function that calls all the other ones
        pi_module_name=f'CFG_{PI}'
        PI_CFG=importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        # Pour toutes les aggrégations temporelles (seulement YEAR pour l'instant)
        for AGG_TIME in AGGS_TIME:
            # Pour tous les espaces d'aggrégation (PLAN, SECTION)
            for AGG_SPACE in AGGS_SPACE:
                if self.logger:
                    self.logger.info('  ->' + AGG_SPACE)
                print('  ->',AGG_SPACE)
                list_var=list(PI_CFG.dct_var.keys())
                columns=[AGG_TIME]
                for var in list_var:
                    stats=PI_CFG.var_agg_stat[var]
                    for s in stats:
                        stat=var+'_'+s
                        columns.append(stat)
                # Aggrégation
                if AGG_TIME=='YEAR':
                    # PLAN
                    if AGG_SPACE=='PLAN':
                        # Pour tous les plans dans les config du PI
                        for space in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if space in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future

                            if self.logger:
                                self.logger.info('    -->' + space)
                            print('    -->',space)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, space)
                            # Si les résultats existent déjà, skipper
                            if os.path.exists(path_res):
                                if self.logger:
                                    self.logger.info(f'AGG level of {AGG_SPACE} for plan {space} already exists skipping....')
                                else:
                                    print(f'AGG level of {AGG_SPACE} for plan {space}  already exists skipping....')
                                continue
                            # Nom du fichier final
                            res_name=f'{PI}_{AGG_TIME}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                            agg_year_param=os.path.join(self.ISEE_RES, PI, space)
                            self.AGG_SPACE_YEAR(path_res, res_name, columns, AGG_TIME, AGG_SPACE, PI, space, list_var, stats, agg_year_param ,'', PI_CFG, years_list)
                    # SECTION
                    elif AGG_SPACE=='SECTION':
                        # Pour tous les plans dans les config du PI
                        for p in PI_CFG.available_plans+PI_CFG.available_baselines:
                            # Extraire la liste des années
                            if p in PI_CFG.plans_hist:
                                years_list = PI_CFG.available_years_hist
                            else:
                                years_list = PI_CFG.available_years_future
                            # Pour toutes les sections, aggréger pour le plan courant
                            for space in PI_CFG.available_sections:
                                if self.logger:
                                    self.logger.info('    -->' + p + ' ' + space)
                                print('    -->',p, space)

                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                # Si les résultats existent déjà, skipper
                                if os.path.exists(path_res):
                                    if self.logger:
                                        self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    else:
                                        print(f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue

                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.parquet'
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


# tiled=POST_PROCESS_2D_tiled(cfg.pis_2D_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

# not_tiled=POST_PROCESS_2D_not_tiled(cfg.pis_2D_not_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

# pi_1D=POST_PROCESS_1D(cfg.pis_1D, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)

# for pi in not_tiled.pis:
#     print(pi)
#     not_tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'])
#     # not_tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION'])

# for pi in tiled.pis:
#     print(pi)
#     tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE', 'PT_ID'])
    # tiled.agg_2D_space(pi, ['YEAR'], ['PLAN', 'SECTION', 'TILE'])
    # tiled.agg_2D_space(pi, ['YEAR'], ['PLAN'])

# for pi in pi_1D.pis:
#     print(pi)
#     pi_1D.agg_1D_space(pi, ['YEAR'], ['PLAN', 'SECTION'])

# quit()



