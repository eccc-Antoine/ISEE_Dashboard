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
            if file.endswith(".feather"):
                feather_path = os.path.join(subdir, file)

                # Build the destination path with same relative structure
                rel_path = os.path.relpath(feather_path, src_root)
                parquet_path = os.path.join(dst_root, rel_path).replace(".feather", ".parquet")

                # Ensure destination directory exists
                os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

                print(f"Converting: {feather_path} -> {parquet_path}")
                try:
                    # Load feather
                    df = pd.read_feather(feather_path)
                    # tile_id = os.path.basename(subdir)
                    # print(tile_id)
                    # df['tile'] = tile_id

                    # Save parquet with snappy compression
                    df.to_parquet(parquet_path, engine="pyarrow", index=False, compression="snappy")

                except Exception as e:
                    print(f"⚠️ Failed to convert {feather_path}: {e}")



# Example usage

PI='ONZI_1D'

convert_feather_to_parquet(
    src_root=fr"P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\{PI}",
    dst_root=fr"F:\GLAM_DASHBOARD\PARQUET_TEST\{PI}"
)
