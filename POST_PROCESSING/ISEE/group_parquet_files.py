import pandas as pd
import numpy as np
import os
import importlib
import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from azure.storage.blob import BlobServiceClient

unique_pi_module_name = 'CHNI_2D'
unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{unique_pi_module_name}')


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

def group_parquet_files(folder, container, sas_token):

    division = folder.split('/')[-2]
    print(division)
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
                continue
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

    else: return pd.DataFrame()

    df_final = pd.concat(df_all).reset_index(drop=True)
    return df_final


blob_service_client = BlobServiceClient(f'https://eccciseedashboardst.blob.core.windows.net', credential = access_key)
container = blob_service_client.get_container_client('dukc-db')
folder = f'test/{unique_pi_module_name}/YEAR/PLAN/'

df = group_parquet_files(folder, container, sas_token)
save_parquet_to_blob(container, df, f'{folder}{unique_pi_module_name}_all_plans.parquet')

folder = f'test/{unique_pi_module_name}/YEAR/TILE/'
df = group_parquet_files(folder, container, sas_token)
save_parquet_to_blob(container, df, f'{folder}{unique_pi_module_name}_all_tiles.parquet')
