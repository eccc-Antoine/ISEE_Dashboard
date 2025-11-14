import pandas as pd
import numpy as np
import os
import importlib
import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from azure.storage.blob import BlobServiceClient


# 2025-10-20
# There's currently one parquet file per plan, section, tiles, etc.
# Let's create one file to avoid opening, reading and closing multiple files.

def read_parquet_from_blob(container, blob_name):
    stream = io.BytesIO()
    data = container.download_blob(blob_name)
    data.readinto(stream)
    df = pd.read_parquet(stream,engine='pyarrow')
    if 'index' in df.columns:
        df.set_index('index',inplace=True)
    return df

def save_parquet_to_blob(container, df, blob_name):
    # parquet_file = io.BytesIO()
    data = df.to_parquet()
    blob_client = container.get_blob_client(blob_name)
    blob_client.upload_blob(data,overwrite=True)
    return

def group_parquet_files(folder, container):

    division = folder.split('/')[-2]
    print('-->',division)
    df_all = []
    if division == 'PLAN':
        for plan_path in container.walk_blobs(folder, delimiter='/'):
            if plan_path.name.endswith('.parquet'):
                continue
            plan = plan_path.name.split('/')[-2]
            blob_list = container.list_blobs(name_starts_with=plan_path.name)

            for blob in blob_list:
                df = read_parquet_from_blob(container, blob.name)
                df['PLAN'] = plan
                df_all.append(df)

    elif division == 'TILE':
        for plan_path in container.walk_blobs(folder, delimiter='/'):
            if plan_path.name.endswith('.parquet'):
                continue # It's a file, skip
            for section_path in container.walk_blobs(plan_path.name, delimiter='/'):
                for tile_path in container.walk_blobs(section_path.name, delimiter='/'):
                    plan = plan_path.name.split('/')[-2]
                    section = section_path.name.split('/')[-2]
                    tile = tile_path.name.split('/')[-2]
                    blob_list = container.list_blobs(name_starts_with=tile_path.name)

                    for blob in blob_list:
                        df = read_parquet_from_blob(container, blob.name)
                        df['PLAN'] = plan
                        df['SECTION'] = section
                        df['TILE'] = tile
                        df_all.append(df)

    elif division == 'SECTION':
        for plan_path in container.walk_blobs(folder, delimiter='/'):
            if plan_path.name.endswith('.parquet'):
                continue # It's a file, skip
            for section_path in container.walk_blobs(plan_path.name, delimiter='/'):
                plan = plan_path.name.split('/')[-2]
                section = section_path.name.split('/')[-2]
                blob_list = container.list_blobs(name_starts_with=section_path.name)

                for blob in blob_list:
                    df = read_parquet_from_blob(container, blob.name)
                    df['PLAN'] = plan
                    df['SECTION'] = section
                    df_all.append(df)

    else: return pd.DataFrame()

    df_final = pd.concat(df_all).reset_index(drop=True)
    return df_final

# PI=['AYL_2D','BIRDS_2D','CHNI_2D','CWRM_2D','ERIW_MIN_1D','ERIW_MIN_2D','IERM_2D','IXEX_RPI_2D','MFI_2D','NFB_2D','ONZI_OCCUPANCY_1D',
#     'PIKE_2D','ROADS_2D','SAUV_2D','SHORE_PROT_STRUC_1D','TURTLE_1D','WASTE_WATER_2D','WATER_INTAKES_2D','ZIPA_1D']

PI=['TURTLE_1D']


blob_service_client = BlobServiceClient(container_url, credential = access_key)
container = blob_service_client.get_container_client('dukc-db')

for pi in PI:

    print(pi)

    unique_pi_module_name = pi
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{unique_pi_module_name}')

    folder = f'test/{unique_pi_module_name}/YEAR/PLAN/'
    df = group_parquet_files(folder, container)
    save_parquet_to_blob(container, df, f'{folder}{unique_pi_module_name}_ALL_PLANS.parquet')

    folder = f'test/{unique_pi_module_name}/YEAR/SECTION/'
    df = group_parquet_files(folder, container)
    save_parquet_to_blob(container, df, f'{folder}{unique_pi_module_name}_ALL_SECTIONS.parquet')

    if pi[-2:] == '2D':
        folder = f'test/{unique_pi_module_name}/YEAR/TILE/'
        df = group_parquet_files(folder, container)
        save_parquet_to_blob(container, df, f'{folder}{unique_pi_module_name}_ALL_TILES.parquet')
