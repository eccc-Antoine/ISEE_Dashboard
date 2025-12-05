import os
import pandas as pd


def convert_feather_to_parquet(src_root, dst_root):
    """
    Convert all .feather files under src_root into .parquet under dst_root,
    preserving folder structure.

    Parameters:
        src_root (str): Source directory containing feather files.
        dst_root (str): Destination root directory for parquet files.
    """
    for subdir, _, files in os.walk(src_root):
        print(subdir)
        for file in files:

            feather_path = os.path.join(subdir, file)

            # Build the destination path with same relative structure
            rel_path = os.path.relpath(feather_path, src_root)
            if rel_path.endswith(".feather"):
                rel_path = rel_path[:-8]
            parquet_path = os.path.join(dst_root, rel_path) +  ".parquet"

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

            # print(f"Converting: {feather_path} -> {parquet_path}")
            try:
                # Load feather
                df = pd.read_feather(feather_path)

                # Save parquet with snappy compression
                df.to_parquet(parquet_path, engine="pyarrow", index=False, compression="snappy")

            except Exception as e:
                print(f"⚠️ Failed to convert {feather_path}: {e}")



# Example usage

# PI=['AYL_2D','BIRDS_2D','CHNI_2D','CWRM_2D','ERIW_MIN_1D','ERIW_MIN_2D','IERM_2D','IXEX_RPI_2D','MFI_2D','NFB_2D','ONZI_OCCUPANCY_1D',
#     'PIKE_2D','ROADS_2D','SAUV_2D','SHORE_PROT_STRUC_1D','TURTLE_1D','WASTE_WATER_2D','WATER_INTAKES_2D','ZIPA_1D']

PI=['TURTLE_1D']
folder=['PT_ID', 'SECTION', 'PLAN', 'TILE']
combo='A'
print('Feathers to parquet for combo'+combo)
for pi in PI:
    print(pi)
    # for f in folder:
    #     convert_feather_to_parquet(
    #         src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}",
    #         dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}")
    for f in folder:

        for p in plans:
            # print(f)
            # print(f'GERBL2_2014_Combo{combo}_STO_330')
            # convert_feather_to_parquet(
            #     src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_STO_330",
            #     dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_STO_330")
            # print(f'GERBL2_2014_Combo{combo}_RCP45')
            # convert_feather_to_parquet(
            #     src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_RCP45",
            #     dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_RCP45")

            src=fr"P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\{p}"
            dst=fr'F:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\{p}'
            convert_feather_to_parquet(src, dst)

        # print(f'GERBL2_2014_Combo{combo}')
        # convert_feather_to_parquet(
        #     src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}",
        #     dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}")

