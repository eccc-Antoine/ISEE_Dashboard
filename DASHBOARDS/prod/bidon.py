import pandas as pd

df=pd.read_feather(fr"T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW\WL_GLRRM_1D\PreProjectHistorical\USL_US\WL_GLRRM_1D_PreProjectHistorical_USL_US.feather")

print(df.head())

print(list(df))

quit()







# def prep_for_prep_tiles_duckdb(tile_shp, folder, PI_code, scen_code, avail_years, stat, var,
#                                sect_PI, multiplier, start_year, end_year, sas_token, container_url):
#     print('PREP_FOR_PREP_TILES_DUCKDB')
#
#     con = duckdb.connect(database=':memory:')
#
#     shp_url=f"{container_url}/{tile_shp}?{sas_token}"
#
#     gdf_tiles = gpd.read_file(shp_url)
#
#     parquet_files = []
#     for s in sect_PI:
#         for t in CFG_DASHBOARD.dct_tile_sect[s]:
#             df_folder = os.path.join(folder, PI_code, 'YEAR', 'TILE', scen_code, s, str(t))
#             parquet_file = os.path.join(
#                 df_folder,
#                 f'{PI_code}_YEAR_{scen_code}_{s}_{t}_{np.min(avail_years)}_{np.max(avail_years)}.parquet'
#             )
#             parquet_files.append(parquet_file.replace('\\', '/'))
#
#     parquet_urls = [f"{container_url}/{f}?{sas_token}" for f in parquet_files]
#
#     rel = con.read_parquet(parquet_urls)
#
#     con.register("tiles", rel)
#
#     cols = rel.columns
#
#     if f'{var}_mean' in cols:
#
#         if stat == 'mean':
#             agg_expr = f"avg({var}_mean) * {multiplier}"
#         elif stat == 'sum':
#             agg_expr = f"sum({var}_mean) * {multiplier}"
#         elif stat == 'min':
#             agg_expr = f"min({var}_mean) * {multiplier}"
#         elif stat == 'max':
#             agg_expr = f"max({var}_mean) * {multiplier}"
#         else:
#             raise ValueError("Unsupported stat")
#
#     if f'{var}_sum' in cols:
#
#         if stat == 'mean':
#             agg_expr = f"avg({var}_sum) * {multiplier}"
#         elif stat == 'sum':
#             agg_expr = f"sum({var}_sum) * {multiplier}"
#         elif stat == 'min':
#             agg_expr = f"min({var}_sum) * {multiplier}"
#         elif stat == 'max':
#             agg_expr = f"max({var}_sum) * {multiplier}"
#         else:
#             raise ValueError("Unsupported stat")
#
#     sql = f"""
#         SELECT tile,
#                round({agg_expr}, 3) AS VAL
#         FROM tiles
#         WHERE YEAR BETWEEN {start_year} AND {end_year}
#         GROUP BY tile
#     """
#
#     df_stats = con.execute(sql).df()
#
#     df_stats['tile']=df_stats['tile'].astype(int)
#
#     gdf_tiles = gdf_tiles.merge(df_stats, on="tile", how="left")
#
#     gdf_tiles = gdf_tiles.dropna(subset=["VAL"])
#     gdf_tiles = gdf_tiles.loc[gdf_tiles['VAL'] != 0]
#
#     return gdf_tiles