import pandas as pd
import numpy as np
import os
import importlib
import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from azure.storage.blob import BlobServiceClient

def save_parquet_to_blob(container, df, blob_name):
    # parquet_file = io.BytesIO()
    data = df.to_parquet()
    blob_client = container.get_blob_client(blob_name)
    blob_client.upload_blob(data,overwrite=True)
    return

def list_files(folder):
    file_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.parquet'):
                file_list.append(os.path.join(root, file))
    return file_list



blob_service_client = BlobServiceClient(db_url, credential = access_key)
container = blob_service_client.get_container_client('dukc-db')

PI=['AYL_2D','BIRDS_2D','CHNI_2D','CWRM_2D','ERIW_MIN_1D','ERIW_MIN_2D','IERM_2D','IXEX_RPI_2D','MFI_2D','NFB_2D','ONZI_OCCUPANCY_1D',
    'PIKE_2D','ROADS_2D','SAUV_2D','SHORE_PROT_STRUC_1D','TURTLE_1D','WASTE_WATER_2D','WATER_INTAKES_2D','ZIPA_1D']

local_folder = fr"D:\GLAM_DASHBOARD\PARQUET_TEST"

for pi in PI:
    print(pi)
    unique_pi_module_name = pi
    unique_PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.CFG_{unique_pi_module_name}')

    pi_folder = os.path.join(local_folder,pi)
    file_list = list_files(pi_folder)

    for file in file_list:
        df = pd.read_parquet(file)
        if ('TILE' in file) and ('TILE' not in df.columns.to_list()):
            path = file.split('\\')
            df['TILE'] = int(path[-2])
        blob_name = os.path.join('test/',file[31:].replace('\\','/'))
        save_parquet_to_blob(container, df, blob_name)

