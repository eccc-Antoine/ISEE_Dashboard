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

PI=['NFB_2D']
folder='SECTION' # SECTION, PLAN, PT_ID, TILE

for pi in PI:
    print(pi)
    print('GERBL2_2014_ComboB_STO_330')
    convert_feather_to_parquet(
        src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{folder}\GERBL2_2014_ComboB_STO_330",
        dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{folder}\GERBL2_2014_ComboB_STO_330")
    print('GERBL2_2014_ComboB_RCP45')
    convert_feather_to_parquet(
        src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{folder}\GERBL2_2014_ComboB_RCP45",
        dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{folder}\GERBL2_2014_ComboB_RCP45")
    print('GERBL2_2014_ComboB')
    convert_feather_to_parquet(
        src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{folder}\GERBL2_2014_ComboB",
        dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{folder}\GERBL2_2014_ComboB")