import pandas as pd
import numpy as np
import logging
import CFG_POST_PROCESS_ISEE as cfg
from src.ISEE_POSTPROCESS import POST_PROCESS_2D_tiled, POST_PROCESS_2D_not_tiled, POST_PROCESS_1D
from src.FORMAT_DASH_FILES import *
import importlib
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from azure.storage.blob import BlobServiceClient


'''
Format ISEE results for the Dashboard. There're two main steps :
1. Do some aggregation (ISEE_POSTPROCESS)
2. Format the files and upload them to Azure (in parquet format)

You need to modify the config file to choose which PI to post process and upload,
as well as which plan and/or section.

The main progress of the script will be printed in the terminal, the intermediate steps
will be saved in log files (one per pi) for consultation
'''

def main():
    """Main execution function."""

    # Logs
    logger = start_logger(name=cfg.log_name)

    # Azure connection
    azure_access = importlib.import_module("DASHBOARDS.azure_access")
    azure_url = azure_access.azure_url
    access_key = azure_access.access_key

    blob_service_client = BlobServiceClient(azure_url, credential = access_key)
    container = blob_service_client.get_container_client('dukc-db')

    all_pis = cfg.pis_2D_tiled + cfg.pis_2D_not_tiled + cfg.pis_1D
    agg_type = cfg.agg_type # Add to config
    # Check if there are pis
    assert len(all_pis) != 0, 'Input which PI you want to post process in config file'
    # check if all agg_type are valid
    for agg in agg_type:
        assert agg in ['PLAN','SECTION','TILE','PT_ID'], f"{agg} is an invalid aggregation type. Please use ['PLAN','SECTION','TILE','PT_ID']"

    print('Launching Post-Processing for', all_pis)

    # ISEE_POSTPROCESS per type of PI
    # Would be cool if we could parallelized this, but not a priority
    if len(cfg.pis_2D_tiled) != 0:
        tiled=POST_PROCESS_2D_tiled(cfg.pis_2D_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, logger=logger)
        for pi in tiled.pis:
            print(f'Post processing {pi}...')
            tiled.agg_2D_space(pi, ['YEAR'], agg_type)

    if len(cfg.pis_2D_not_tiled) != 0:
        not_tiled=POST_PROCESS_2D_not_tiled(cfg.pis_2D_not_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, logger=logger)
        for pi in not_tiled.pis:
            print(f'Post processing {pi}...')
            not_tiled.agg_2D_space(pi, ['YEAR'], agg_type)

    if len(cfg.pis_1D) != 0:
        pi_1D=POST_PROCESS_1D(cfg.pis_1D, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep)
        for pi in pi_1D.pis:
            print(f'Post processing {pi}...')
            agg_type_1D = [agg for agg in agg_type if agg in ['PLAN', 'SECTION']]
            pi_1D.agg_1D_space(pi, ['YEAR'], agg_type_1D)

    # group and upload to Azure
    print('Group parquet for', agg_type)
    # We need to group all available plans, sections and tiles, even if only one section or plan is ran
    for pi in all_pis:
        print('  ->',pi)
        for agg in agg_type:
            # We don't group PT_ID files
            if agg == 'PT_ID':
                continue
            # There's no TILE folder for 1D PIs
            if agg == 'TILE' and pi[-2:] == '1D':
                continue

            folder = f'{cfg.POST_PROCESS_RES}/{pi}/YEAR/{agg}/'
            df = group_parquet_files_local(folder)
            df.to_parquet(f'{folder}{pi}_ALL_{agg}S.parquet', engine="pyarrow", index=False, compression="snappy")

    # Upload to Azure
    # Only upload new files, based on the plans + sections and ALL files
    print('Uploading parquet to Azure...')
    for pi in all_pis:
        print('  ->',pi)

        pi_folder = os.path.join(cfg.POST_PROCESS_RES,pi)
        file_list = list_files(folder) + list_files(folder, extension='.feather')

        # Only the concerned aggegation levels
        file_list = [f for f in file_list if any(agg in f for agg in agg_type)]

        # Only the concerned plans + ALL
        file_list = [f for f in file_list if ('ComboA' in f) | ('ComboB' in f) | ('ALL' in f)] # to modify
    #     # Only the concerned sections
    #     file_list = [f for f in file_list if ('ComboA' in f) | ('ComboB' in f)] # to modify

        for file in file_list:
            blob_name = os.path.join('test/',file[file.find(pi):].replace('\\','/'))
            save_parquet_to_blob(container, file, blob_name)

    return
if __name__ == "__main__":
    main()


