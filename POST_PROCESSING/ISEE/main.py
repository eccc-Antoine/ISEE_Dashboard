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
will be saved in log files for consultation
'''

pi_type = {'tiled' : ['SAUV_2D', 'IERM_2D', 'CWRM_2D', 'IXEX_RPI_2D', 'CHNI_2D', 'ERIW_MIN_2D', 'PIKE_2D'],
           'not_tiled' : ['WASTE_WATER_2D', 'AYL_2D', 'BIRDS_2D', 'MFI_2D', 'NFB_2D', 'ROADS_2D', 'WATER_INTAKES_2D'],
           '1d' : ['SHORE_PROT_STRUC_1D', 'ERIW_MIN_1D', 'ONZI_OCCUPANCY_1D', 'TURTLE_1D', 'WL_GLRRM_1D', 'WL_ISEE_1D', 'ZIPA_1D']}

def concat_and_upload(pi,logger,container):
    # group and upload to Azure
    logger.info(f'Group parquet for {cfg.agg_type}')
    print('Group parquet for', cfg.agg_type)
    # We need to group all available plans, sections and tiles, even if only one section or plan is ran
    logger.info(f'  -> {pi}')
    print('  ->',pi)
    for agg in cfg.agg_type:
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
    logger.info('Uploading parquet to Azure...')
    print('Uploading parquet to Azure...')
    print('  ->',pi)
    logger.info(f'  -> {pi}')

    pi_folder = os.path.join(cfg.POST_PROCESS_RES,pi)
    file_list = list_files(pi_folder) + list_files(pi_folder, extension='.feather')

    # Only the concerned aggegation levels
    file_list = [f for f in file_list if any(agg in f for agg in cfg.agg_type)]

    # Only the concerned plans + ALL
    file_list = [f for f in file_list if any(plan in f for plan in cfg.plans) or ('ALL' in f)]

    for file in file_list:
        blob_name = os.path.join('test/',file[file.find(pi):].replace('\\','/'))
        save_parquet_to_blob(container, file, blob_name)

    return

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

    # Check if pis are the right type
    for pi in cfg.pis_2D_tiled:
        assert pi in pi_type['tiled'], f"PI {pi} is not a tiled PI. Please check your config file."

    for pi in cfg.pis_2D_not_tiled:
        assert pi in pi_type['not_tiled'], f"PI {pi} is not a non-tiled PI. Please check your config file."

    for pi in cfg.pis_1D:
        assert pi in pi_type['1d'], f"PI {pi} is not a 1D PI. Please check your config file."

    all_pis = cfg.pis_2D_tiled + cfg.pis_2D_not_tiled + cfg.pis_1D
    agg_type = cfg.agg_type # Add to config
    # Check if there are pis
    assert len(all_pis) != 0, 'Input which PI you want to post process in config file'
    # check if all agg_type are valid
    for agg in agg_type:
        assert agg in ['PLAN','SECTION','TILE','PT_ID'], f"{agg} is an invalid aggregation type. Please use ['PLAN','SECTION','TILE','PT_ID']"

    logger.info(f'Starting Post-Processing for {all_pis} with aggregation types {agg_type} for plans {cfg.plans}')
    print('Launching Post-Processing for', all_pis)

    # ISEE_POSTPROCESS per type of PI
    # Would be cool if we could parallelized this, but not a priority
    if len(cfg.pis_2D_tiled) != 0:
        tiled=POST_PROCESS_2D_tiled(cfg.pis_2D_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, logger=logger)
        for pi in tiled.pis:

            logger.info(f'Post processing {pi}...')
            print(f'Post processing {pi}...')
            tiled.agg_2D_space(pi, ['YEAR'], agg_type)
            concat_and_upload(pi,logger,container)
            logger.info(f'Post processing of {pi} finished.')

    if len(cfg.pis_2D_not_tiled) != 0:
        not_tiled=POST_PROCESS_2D_not_tiled(cfg.pis_2D_not_tiled, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, logger=logger)
        for pi in not_tiled.pis:
            logger.info(f'Post processing {pi}...')
            print(f'Post processing {pi}...')
            not_tiled.agg_2D_space(pi, ['YEAR'], agg_type)
            concat_and_upload(pi,logger,container)
            logger.info(f'Post processing of {pi} finished.')

    if len(cfg.pis_1D) != 0:
        pi_1D=POST_PROCESS_1D(cfg.pis_1D, cfg.ISEE_RES, cfg.POST_PROCESS_RES, cfg.sep, logger=logger)
        for pi in pi_1D.pis:
            logger.info(f'Post processing {pi}...')
            print(f'Post processing {pi}...')
            agg_type_1D = [agg for agg in agg_type if agg in ['PLAN', 'SECTION']]
            pi_1D.agg_1D_space(pi, ['YEAR'], agg_type_1D)
            concat_and_upload(pi,logger,container)
            logger.info(f'Post processing of {pi} finished.')

    return

if __name__ == "__main__":
    main()


