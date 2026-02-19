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
import duckdb
import time
import glob
import pyarrow.feather as feather
import pyarrow.parquet as pq
import pyarrow as pa
import pyarrow.dataset as ds
print(cfg)
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Environment path:", sys.prefix)
print("Installed site-packages:", sysconfig.get_paths()["purelib"])
print("Environment variables (conda/venv):", os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX"))

class POST_PROCESS_2D_tiled:
    def __init__(self, pis, ISEE_RES_parquet, POST_PROCESS_RES, sep, logger=None):
        self.pis = pis
        self.ISEE_RES_parquet = ISEE_RES_parquet
        self.POST_PROCESS_RES = POST_PROCESS_RES
        self.sep = sep
        self.logger = logger

    def convert_feather_to_parquet(self, src_root, dst_root, PI):
        """
        Convert all .feather files under src_root into .parquet under dst_root,
        preserving folder structure.

        Parameters:
            src_root (str): Source directory containing feather files.
            dst_root (str): Destination root directory for parquet files.
        """
        for subdir, _, files in os.walk(src_root):
            for file in files:

                if PI not in file:
                    continue

                feather_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(feather_path, src_root)
                if rel_path.endswith(".feather"):
                    rel_path = rel_path[:-8]
                parquet_path = os.path.join(dst_root, rel_path) + ".parquet"

                os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

                try:
                    df = pd.read_feather(feather_path)
                    df.to_parquet(parquet_path, engine="pyarrow", index=False, compression="snappy")

                except Exception as e:
                    print(f"⚠️ Failed to convert {feather_path}: {e}")

    def _build_agg_sql(self, list_var, PI_CFG):
        exprs = []
        for var in list_var:
            for stat in PI_CFG.var_agg_stat[var]:
                exprs.append(f"{stat.upper()}({var}) AS {var}_{stat}")
        return ",\n".join(exprs)


    def create_agg_space_table(self, AGG_SPACE, AGG_TIME, list_var, PI_CFG, space):
        print(f'creating results table aggregated by {AGG_SPACE} {AGG_TIME}...')
        agg_expr = self._build_agg_sql(list_var, PI_CFG)
        self.con.execute(f"""DROP TABLE IF EXISTS wl_isee_yearly;
                            CREATE TABLE wl_isee_yearly AS
                            SELECT
                                {AGG_SPACE},
                                {AGG_TIME},
                                {agg_expr}
                            FROM wl_isee_{space}
                            GROUP BY {AGG_SPACE}, {AGG_TIME};""")

    def AGG_SPACE_YEAR(self, path_res, res_name, AGG_SPACE, space):
        os.makedirs(path_res)
        df=self.con.execute(f"""SELECT *
                            FROM wl_isee_yearly
                            WHERE {AGG_SPACE} = ?
                            ORDER BY YEAR;""", [str(space)]).df()

        df.to_parquet(os.path.join(path_res, res_name))

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
        var_cols=list(PI_CFG.dct_var.keys())
        cols=['PT_ID']+var_cols
        cols_sql=", ".join(cols)
        plans = list(dict.fromkeys(PI_CFG.available_plans + PI_CFG.available_baselines))

        for p in plans:

            print( f'--> processing plan {p}' )

            if p in PI_CFG.plans_hist:
                years_list = PI_CFG.available_years_hist
            else:
                years_list = PI_CFG.available_years_future

            src_root=os.path.join(cfg.ISEE_RES, PI, p)
            dst_root=os.path.join(cfg.ISEE_RES_parquet, PI, p)

            if not os.path.exists(dst_root):
                print(f'parquet files for plan {p} don t exists, need to create it')
                self.convert_feather_to_parquet(src_root, dst_root, PI)

            # plus rapide si on cree la bd localement plutot que sur le NAS ou projet
            path_db = os.path.join(cfg.duckbd_path, fr"{PI}_{p}_database_2.duckdb")

            db_exists = os.path.exists(path_db)

            self.con = duckdb.connect(path_db)
            self.con.execute(f"PRAGMA threads={os.cpu_count()}")
            self.con.execute("PRAGMA enable_progress_bar=false")
            self.con.execute("PRAGMA preserve_insertion_order=false")

            if not db_exists:
                start = time.perf_counter()
                print(f'bulding plan {p} table for the first time... it might take a while')

                base = Path(os.path.join(cfg.ISEE_RES_parquet, PI, p))

                parquet_glob = base.as_posix() + "/**/*.parquet"

                self.con.execute(f"""DROP VIEW IF EXISTS wl_isee_{p};
                
                CREATE TABLE wl_isee_{p} AS
                WITH files AS (
                                SELECT
                                *,
                                replace(filename, '\\', '/') AS fname
                                FROM read_parquet('{parquet_glob}', filename=true))
                SELECT
                    {cols_sql},
                    split_part(fname, '/', -4) AS PLAN,
                    split_part(fname, '/', -3) AS SECTION,
                    split_part(fname, '/', -2) AS YEAR,
                    TRY_CAST(split_part(fname, '_', -2) AS INTEGER) AS TILE
                FROM files;""")


                elapsed = time.perf_counter() - start
                print(f"✔ it took  {elapsed:.2f} seconds to build the table")

            else:
                print('db already exists, no need to create it')

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
                            if self.logger:
                                self.logger.info(f'    -->{p}')
                            print('    -->',p)
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            res_name=f'{PI}_{AGG_TIME}_{p}_{min(years_list)}_{max(years_list)}.parquet'

                            if os.path.exists(path_res):
                                if self.logger:
                                    self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} already exists skipping....')
                                else:
                                    print(f'AGG level of {AGG_SPACE} for plan {p} already exists skipping....')
                                continue
                            else:
                                # Aggréger les résulats par plan et par année
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)
                                self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, p)
                        # SECTION
                        elif AGG_SPACE=='SECTION':
                            path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            if os.path.exists(path_res):
                                print(f'aggregation by {AGG_SPACE}, already exists, skipping...')
                                continue
                            else:
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)
                            for space in PI_CFG.available_sections:
                                if self.logger:
                                    self.logger.info(f'    -->{space}')
                                print('    -->',space)
                                path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name=f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                if os.path.exists(path_res):
                                    if self.logger:
                                        self.logger.info(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    else:
                                        print(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue
                                else:
                                    self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, space)

                        # TILE
                        elif AGG_SPACE=='TILE':
                            path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            if os.path.exists(path_res):
                                print(f'aggregation by {AGG_SPACE} for plan {p}, already exists, skipping...')
                                continue
                            else:
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)

                            # Pour toutes les sections
                            for s in PI_CFG.available_sections:
                                # Pour toutes les tuiles, aggréger pour le plan courant
                                for space in cfg.dct_tile_sect[s]:
                                    if self.logger:
                                        self.logger.info('    -->' + p + ' ' + s + ' ' + str(space))
                                    print('    -->',p, s, space)
                                    space=str(space)
                                    path_res=os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    res_name = f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                    # Skip si les résultats existent déjà
                                    if os.path.exists(path_res):
                                        if self.logger:
                                            self.logger.info(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        else:
                                            print(f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        continue
                                    else:
                                        self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, space)

class POST_PROCESS_2D_not_tiled:
    def __init__(self, pis, ISEE_RES_parquet, POST_PROCESS_RES, sep, logger=None):

        self.pis=pis
        self.ISEE_RES_parquet = ISEE_RES_parquet
        self.POST_PROCESS_RES=POST_PROCESS_RES
        self.sep=sep
        self.logger=logger

    def convert_feather_to_parquet(self, src_root, dst_root, PI):
        """
        Convert all .feather files under src_root into .parquet under dst_root,
        preserving folder structure.

        Parameters:
            src_root (str): Source directory containing feather files.
            dst_root (str): Destination root directory for parquet files.
        """
        for subdir, _, files in os.walk(src_root):
            for file in files:

                if PI not in file:
                    continue

                feather_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(feather_path, src_root)
                if rel_path.endswith(".feather"):
                    rel_path = rel_path[:-8]
                parquet_path = os.path.join(dst_root, rel_path) + ".parquet"

                os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

                try:
                    df = pd.read_feather(feather_path)
                    df.to_parquet(parquet_path, engine="pyarrow", index=False, compression="snappy")

                except Exception as e:
                    print(f"⚠️ Failed to convert {feather_path}: {e}")

    def _build_agg_sql(self, list_var, PI_CFG):
        exprs = []
        for var in list_var:
            for stat in PI_CFG.var_agg_stat[var]:
                exprs.append(f"{stat.upper()}({var}) AS {var}_{stat}")
        return ",\n".join(exprs)

    def create_agg_space_table(self, AGG_SPACE, AGG_TIME, list_var, PI_CFG, space):
        print(f'creating results table aggregated by {AGG_SPACE} {AGG_TIME}...')
        agg_expr = self._build_agg_sql(list_var, PI_CFG)
        self.con.execute(f"""DROP TABLE IF EXISTS wl_isee_yearly;
                            CREATE TABLE wl_isee_yearly AS
                            SELECT
                                {AGG_SPACE},
                                {AGG_TIME},
                                {agg_expr}
                            FROM wl_isee_{space}
                            GROUP BY {AGG_SPACE}, {AGG_TIME};""")

    def AGG_SPACE_YEAR(self, path_res, res_name, AGG_SPACE, space):
        os.makedirs(path_res)
        df=self.con.execute(f"""SELECT *
                            FROM wl_isee_yearly
                            WHERE {AGG_SPACE} = ?
                            ORDER BY YEAR;""", [str(space)]).df()

        df.to_parquet(os.path.join(path_res, res_name))

    def agg_2D_space(self, PI, AGGS_TIME, AGGS_SPACE):
        '''
        PI = PI accronym (ex. Northern Pike = ESLU_2D)
        VAR = VAR1, VAR2 ... VARx which corresponds to VAR names in PI's metadata
        AGGS_TIME = level of aggregation over time : list of values amongst ['YEAR', 'QM'] QM not available yet
        AGGS_SPACE = level of aggregation over space : list of values amongst [ 'PLAN', 'SECTION', 'TILE']
        stats = stat for aggregated values ['sum'], ['mean'] or ['sum', 'mean']
        '''
        # This is the main function that calls all the other ones
        pi_module_name = f'CFG_{PI}'
        PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
        # Pour toutes les aggrégations temporelles (seulement YEAR pour l'instant)

        var_cols = list(PI_CFG.dct_var.keys())
        cols = ['PT_ID', 'TILE', 'SECTION'] + var_cols
        cols_sql = ", ".join(cols)
        plans = list(dict.fromkeys(PI_CFG.available_plans + PI_CFG.available_baselines))

        for p in plans:

            if p in PI_CFG.plans_hist:
                years_list = PI_CFG.available_years_hist
            else:
                years_list = PI_CFG.available_years_future

            print(f'--> processing plan {p}')

            src_root = os.path.join(cfg.ISEE_RES, PI, p)
            dst_root = os.path.join(cfg.ISEE_RES_parquet, PI, p)

            if not os.path.exists(dst_root):
                print(f'parquet files for plan {p} don t exists, need to create it')
                self.convert_feather_to_parquet(src_root, dst_root, PI)

            # plus rapide si on cree la bd localement plutot que sur le NAS ou projet
            path_db = os.path.join(cfg.duckbd_path, fr"{PI}_{p}_database_2.duckdb")

            db_exists = os.path.exists(path_db)

            self.con = duckdb.connect(path_db)
            self.con.execute(f"PRAGMA threads={os.cpu_count()}")
            self.con.execute("PRAGMA enable_progress_bar=false")
            self.con.execute("PRAGMA preserve_insertion_order=false")
            #self.con.execute(fr"PRAGMA temp_directory={cfg.temp_folder}")

            if not db_exists:
                start = time.perf_counter()
                print(f'bulding plan {p} table for the first time... it might take a while')

                base = Path(os.path.join(cfg.ISEE_RES_parquet, PI, p))

                parquet_glob = base.as_posix() + "/**/*.parquet"

                self.con.execute(f"""DROP VIEW IF EXISTS wl_isee_{p};
    
                CREATE TABLE wl_isee_{p} AS
                WITH files AS (
                                SELECT
                                *,
                                replace(filename, '\\', '/') AS fname
                                FROM read_parquet('{parquet_glob}', filename=true))
                SELECT
                    {cols_sql},
                    split_part(fname, '/', -2) AS PLAN,
                    TRY_CAST(SUBSTRING(split_part(fname, '_', -1), 1, 4) AS INTEGER) AS YEAR
                FROM files;""")

                elapsed = time.perf_counter() - start
                print(f"✔ it took  {elapsed:.2f} seconds to build the table")

                print(self.con.execute(f"""SELECT *
                FROM
                wl_isee_{p}
                LIMIT
                10;""").df())

                print(self.con.execute(f"""DESCRIBE
                wl_isee_{p};""").df())


            else:
                print('db already exists, no need to create it')

            for AGG_TIME in AGGS_TIME:
                # Pour tous les espaces d'aggrégation (PLAN, SECTION, TILE, PT_ID)
                for AGG_SPACE in AGGS_SPACE:
                    if self.logger:
                        self.logger.info('  ->' + AGG_SPACE)
                    print('  ->', AGG_SPACE)
                    list_var = list(PI_CFG.dct_var.keys())
                    stats = []
                    columns = [AGG_TIME]
                    for var in list_var:
                        stats = PI_CFG.var_agg_stat[var]
                        for s in stats:
                            stat = var + '_' + s
                            columns.append(stat)

                    # Aggrégation
                    if AGG_TIME == 'YEAR':
                        # PLAN
                        if AGG_SPACE == 'PLAN':

                            if self.logger:
                                self.logger.info(f'    -->{p}')
                            print('    -->', p)

                            res_name = f'{PI}_{AGG_TIME}_{p}_{min(years_list)}_{max(years_list)}.parquet'
                            path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            # Si les résultats existent déjà, skipper
                            if os.path.exists(path_res):
                                if self.logger:
                                    self.logger.info(
                                        f'AGG level of {AGG_SPACE} for plan {p} already exists skipping....')
                                else:
                                    print(f'AGG level of {AGG_SPACE} for plan {p}  already exists skipping....')
                                continue
                            else:
                                # Aggréger les résulats par plan et par année
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)
                                self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, p)

                        # SECTION
                        elif AGG_SPACE == 'SECTION':
                            path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            if os.path.exists(path_res):
                                print(f'aggregation by {AGG_SPACE}, already exists, skipping...')
                                continue
                            else:
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)

                            for space in PI_CFG.available_sections:
                                if self.logger:
                                    self.logger.info(f'    -->{space}')
                                print('    -->', space)
                                path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name = f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                # Si les résultats existent déjà, skipper
                                if os.path.exists(path_res):
                                    if self.logger:
                                        self.logger.info(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    else:
                                        print(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue
                                else:
                                    self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, space)

                        # TILE
                        elif AGG_SPACE == 'TILE':
                            path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            if os.path.exists(path_res):
                                print(f'aggregation by {AGG_SPACE} for plan {p}, already exists, skipping...')
                                continue
                            else:
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)

                            for s in PI_CFG.available_sections:
                                # Pour toutes les tuiles, aggréger pour le plan courant
                                for space in cfg.dct_tile_sect[s]:
                                    if self.logger:
                                        self.logger.info('    -->' + p + ' ' + s + ' ' + str(space))
                                    print('    -->', p, s, space)
                                    space = str(space)
                                    path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, s, space)
                                    res_name = f'{PI}_{AGG_TIME}_{p}_{s}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                    # Skip si les résultats existent déjà
                                    if os.path.exists(path_res):
                                        if self.logger:
                                            self.logger.info(
                                                f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        else:
                                            print(
                                                f'AGG level of {AGG_SPACE} for plan {p} and section {s} and tile {space} already exists skipping....')
                                        continue
                                    else:
                                        self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, space)

class POST_PROCESS_1D:
    def __init__(self, pis, ISEE_RES_parquet, POST_PROCESS_RES, sep, logger=None):

        self.pis = pis
        self.ISEE_RES_parquet = ISEE_RES_parquet
        self.POST_PROCESS_RES = POST_PROCESS_RES
        self.sep = sep
        self.logger = logger

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

    def convert_feather_to_parquet(self, src_root, dst_root, PI):
        """
        Convert all .feather files under src_root into .parquet under dst_root,
        preserving folder structure.

        Parameters:
            src_root (str): Source directory containing feather files.
            dst_root (str): Destination root directory for parquet files.
        """
        for subdir, _, files in os.walk(src_root):
            for file in files:

                print(PI)

                if PI not in file:
                    continue

                feather_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(feather_path, src_root)
                if rel_path.endswith(".feather"):
                    rel_path = rel_path[:-8]
                parquet_path = os.path.join(dst_root, rel_path) + ".parquet"

                print(parquet_path)

                os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

                try:
                    df = pd.read_feather(feather_path)
                    df.to_parquet(parquet_path, engine="pyarrow", index=False, compression="snappy")

                except Exception as e:
                    print(f"⚠️ Failed to convert {feather_path}: {e}")

    def _build_agg_sql(self, list_var, PI_CFG):
        exprs = []
        for var in list_var:
            for stat in PI_CFG.var_agg_stat[var]:
                exprs.append(f"{stat.upper()}({var}) AS {var}_{stat}")
        return ",\n".join(exprs)

    def create_agg_space_table(self, AGG_SPACE, AGG_TIME, list_var, PI_CFG, space):
        print(f'creating results table aggregated by {AGG_SPACE} {AGG_TIME}...')
        agg_expr = self._build_agg_sql(list_var, PI_CFG)
        self.con.execute(f"""DROP TABLE IF EXISTS wl_isee_yearly;
                            CREATE TABLE wl_isee_yearly AS
                            SELECT
                                {AGG_SPACE},
                                {AGG_TIME},
                                {agg_expr}
                            FROM wl_isee_{space}
                            GROUP BY {AGG_SPACE}, {AGG_TIME};""")

    def AGG_SPACE_YEAR(self, path_res, res_name, AGG_SPACE, space):
        os.makedirs(path_res)
        df = self.con.execute(f"""SELECT *
                            FROM wl_isee_yearly
                            WHERE {AGG_SPACE} = ?
                            ORDER BY YEAR;""", [str(space)]).df()

        df.to_parquet(os.path.join(path_res, res_name))

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

        var_cols = list(PI_CFG.dct_var.keys())
        cols = ['YEAR'] + var_cols
        cols_sql = ", ".join(cols)
        plans = list(dict.fromkeys(PI_CFG.available_plans + PI_CFG.available_baselines))

        for p in plans:

            print(f'--> processing plan {p}')

            if p in PI_CFG.plans_hist:
                years_list = PI_CFG.available_years_hist
            else:
                years_list = PI_CFG.available_years_future

            src_root = os.path.join(cfg.ISEE_RES, PI, p)
            dst_root = os.path.join(cfg.ISEE_RES_parquet, PI, p)

            if not os.path.exists(dst_root):
                print(f'parquet files for plan {p} don t exists, need to create it')
                print(src_root, dst_root, PI)
                self.convert_feather_to_parquet(src_root, dst_root, PI)

            # plus rapide si on cree la bd localement plutot que sur le NAS ou projet
            path_db = os.path.join(cfg.duckbd_path, fr"{PI}_{p}_database_2.duckdb")

            db_exists = os.path.exists(path_db)

            self.con = duckdb.connect(path_db)
            self.con.execute(f"PRAGMA threads={os.cpu_count()}")
            self.con.execute("PRAGMA enable_progress_bar=false")
            self.con.execute("PRAGMA preserve_insertion_order=false")
            # self.con.execute(fr"PRAGMA temp_directory={cfg.temp_folder}")

            if not db_exists:
                start = time.perf_counter()
                print(f'bulding plan {p} table for the first time... it might take a while')

                base = Path(os.path.join(cfg.ISEE_RES_parquet, PI, p))

                parquet_glob = base.as_posix() + "/**/*.parquet"

                self.con.execute(f"""DROP VIEW IF EXISTS wl_isee_{p};

                CREATE TABLE wl_isee_{p} AS
                WITH files AS (
                                SELECT
                                *,
                                replace(filename, '\\', '/') AS fname
                                FROM read_parquet('{parquet_glob}', filename=true))
                SELECT
                    {cols_sql},
                    split_part(fname, '/', -2) AS SECTION,
                    split_part(fname, '/', -3) AS PLAN
                FROM files;""")

                elapsed = time.perf_counter() - start
                print(f"✔ it took  {elapsed:.2f} seconds to build the table")

                print(self.con.execute(f"""SELECT *
                FROM
                wl_isee_{p}
                LIMIT
                10;""").df())

                print(self.con.execute(f"""DESCRIBE
                wl_isee_{p};""").df())

            else:
                print('db already exists, no need to create it')

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
                            if self.logger:
                                self.logger.info(f'    -->{p}')
                            print('    -->', p)
                            res_name = f'{PI}_{AGG_TIME}_{p}_{min(years_list)}_{max(years_list)}.parquet'
                            path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            # Si les résultats existent déjà, skipper
                            if os.path.exists(path_res):
                                if self.logger:
                                    self.logger.info(
                                        f'AGG level of {AGG_SPACE} for plan {p} already exists skipping....')
                                else:
                                    print(f'AGG level of {AGG_SPACE} for plan {p}  already exists skipping....')
                                continue
                            else:
                                # Aggréger les résulats par plan et par année
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)
                                self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, p)

                        # SECTION
                        elif AGG_SPACE=='SECTION':
                            path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p)
                            if os.path.exists(path_res):
                                print(f'aggregation by {AGG_SPACE}, already exists, skipping...')
                                continue
                            else:
                                self.create_agg_space_table(AGG_SPACE, AGG_TIME, list_var, PI_CFG, p)
                            for space in PI_CFG.available_sections:
                                if self.logger:
                                    self.logger.info(f'    -->{space}')
                                print('    -->', space)
                                path_res = os.path.join(self.POST_PROCESS_RES, PI, AGG_TIME, AGG_SPACE, p, space)
                                res_name = f'{PI}_{AGG_TIME}_{p}_{space}_{min(years_list)}_{max(years_list)}.parquet'
                                # Si les résultats existent déjà, skipper
                                if os.path.exists(path_res):
                                    if self.logger:
                                        self.logger.info(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    else:
                                        print(
                                            f'AGG level of {AGG_SPACE} for plan {p} and section {space} already exists skipping....')
                                    continue
                                else:
                                    self.AGG_SPACE_YEAR(path_res, res_name, AGG_SPACE, space)

                        else:
                            print(f'input AGG_SPACE {AGG_SPACE} is not valid !!')
                            quit()

                    elif AGG_TIME=='QM':
                        ### NOT coded yet!!
                        pass

                    else:
                        pass




