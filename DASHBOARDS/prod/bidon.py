import pandas as pd

# df=pd.read_csv(fr"P:\GLAM\Dashboard\prod\debug_PTID_318433166_VAR2.csv", sep=';')
# print(df.head())
# var='VAR2'
# id=318433166
# val=df.loc[df['PT_ID'] == id, var].head(1).item()
# print(val)
# quit()

# older_space=
# liste_files=[]
# for root, dirs, files in os.walk(folder_space):
#     for name in files:
#         liste_files.append(os.path.join(root, name))
# print(liste_files)
#
#


df=pd.read_feather(fr"P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\WL_ISEE_1D\YEAR\SECTION\GERBL2_2014_ComboC_STO_330\SLR_DS\WL_ISEE_1D_YEAR_GERBL2_2014_ComboC_STO_330_SLR_DS_2011_2070.feather")

print(df.head())

print(list(df))
print(df['YEAR'].unique())


quit()

df2=df.drop(columns='PT_ID')

overall_mean = df2.to_numpy().mean()
print("Overall mean:", overall_mean)

abs_diff = (df2 - overall_mean).abs()

# Find the minimal difference
min_diff = abs_diff.min().min()

# Find all locations (row, column) where the value is closest to the mean
closest_locs = list(zip(*((abs_diff == min_diff).to_numpy().nonzero())))

print(len(closest_locs))



# Map numeric row/col indices to actual labels
closest_positions = [(df2.index[r], df2.columns[c]) for r, c in closest_locs]

# Get the actual value(s)
closest_values = [df2.loc[r, c] for r, c in closest_positions]

closest_positions=closest_positions[0]
closest_values=closest_values[0]
print("Closest positions:", closest_positions)

row=df2.loc[closest_positions]
#val=row[closest_positions[0][1]]
print(row)

id=df['PT_ID'].loc[closest_positions[0]]

print(id)
quit()

print("Closest positions:", closest_positions)
print("Closest values:", closest_values)

# overall_mean = df.drop(columns='PT_ID').mean().mean()
#
# print(overall_mean)

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