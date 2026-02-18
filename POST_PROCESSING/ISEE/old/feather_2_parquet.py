import os
import pandas as pd
import sys
import sysconfig
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Environment path:", sys.prefix)
print("Installed site-packages:", sysconfig.get_paths()["purelib"])
print("Environment variables (conda/venv):", os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX"))
import pyarrow
print(pyarrow.__version__)



def convert_feather_to_parquet(src_root, dst_root):
    """
    Convert all .feather files under src_root into .parquet under dst_root,
    preserving folder structure.

    Parameters:
        src_root (str): Source directory containing feather files.
        dst_root (str): Destination root directory for parquet files.
    """
    for subdir, _, files in os.walk(src_root):
        # print(subdir)
        for file in files:
            print(file)
            feather_path = os.path.join(subdir, file)

            print(feather_path)


            # Build the destination path with same relative structure
            rel_path = os.path.relpath(feather_path, src_root)
            if rel_path.endswith(".feather"):
                rel_path = rel_path[:-8]
            parquet_path = os.path.join(dst_root, rel_path) +  ".parquet"

            print(parquet_path)


            # Ensure destination directory exists
            os.makedirs(os.path.dirname(parquet_path), exist_ok=True)


            # print(f"Converting: {feather_path} -> {parquet_path}")
            try:
                # Load feather
                df = pd.read_feather(feather_path)
                print('ok')
                # Save parquet with snappy compression
                df.to_parquet(parquet_path, engine="pyarrow", index=False, compression="snappy")

            except Exception as e:
                print(f"⚠️ Failed to convert {feather_path}: {e}")
                quit()



# Example usage

# PI=['AYL_2D','BIRDS_2D','CHNI_2D','CWRM_2D','ERIW_MIN_1D','ERIW_MIN_2D','IERM_2D','IXEX_RPI_2D','MFI_2D','NFB_2D','ONZI_OCCUPANCY_1D',
#     'PIKE_2D','ROADS_2D','SAUV_2D','SHORE_PROT_STRUC_1D','TURTLE_1D','WASTE_WATER_2D','WATER_INTAKES_2D','ZIPA_1D']

PI=['ISEE_WL_2D']
folder=['PT_ID', 'SECTION', 'PLAN', 'TILE']
combo='A'
print('Feathers to parquet for combo'+combo)
for pi in PI:
    print(pi)
    # for f in folder:
    convert_feather_to_parquet(
    src_root=fr"T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW\WL_ISEE_2D\Bv7_2014",
    dst_root=fr"T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_PARQUET\WL_ISEE_2D\Bv7_2014")


    # for f in folder:
    #     print(f)
    #     print(f'GERBL2_2014_Combo{combo}_STO_330')
    #     convert_feather_to_parquet(
    #         src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_STO_330",
    #         dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_STO_330")
    #     print(f'GERBL2_2014_Combo{combo}_RCP45')
    #     convert_feather_to_parquet(
    #         src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_RCP45",
    #         dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}_RCP45")
    #     print(f'GERBL2_2014_Combo{combo}')
    #     convert_feather_to_parquet(
    #         src_root=fr"\\ECQCG1JWPASP002\projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}",
    #         dst_root=fr"D:\GLAM_DASHBOARD\PARQUET_TEST\{pi}\YEAR\{f}\GERBL2_2014_Combo{combo}")

