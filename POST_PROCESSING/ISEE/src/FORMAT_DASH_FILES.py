import os
import pandas as pd
import numpy as np
import sys
import logging
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

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

def save_parquet_to_blob(container, file, blob_name):
    # parquet_file = io.BytesIO()
    if file.endswith('.parquet'):
        df = pd.read_parquet(file,engine='pyarrow')
    else:
        df = pd.read_feather(file)
    data = df.to_parquet()
    blob_client = container.get_blob_client(blob_name)
    blob_client.upload_blob(data,overwrite=True)
    return

def list_files(folder, extension='.parquet'):
    file_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(extension):
                file_list.append(os.path.join(root, file))
    return file_list

def group_parquet_files_local(folder):

    division = folder.split('/')[-2]
    print('    -->',division)
    df_all = []
    if division == 'PLAN':
        file_list = list_files(folder) + list_files(folder, extension='.feather')
        file_list = [f.replace('/', '\\') for f in file_list if 'ALL' not in f]

        for f in file_list:
            # print(f)
            plan = f.split('\\')[-2]
            # print(plan)
            if f.endswith('.feather'):
                df = pd.read_feather(os.path.join(folder,plan,f))
            else:
                df = pd.read_parquet(os.path.join(folder,plan,f),engine='pyarrow')
            if 'index' in df.columns:
                df.set_index('index',inplace=True)
            df['PLAN'] = plan
            df_all.append(df)

    elif division == 'TILE':
        file_list = list_files(folder) + list_files(folder, extension='.feather')
        file_list = [f.replace('/', '\\') for f in file_list if 'ALL' not in f]

        # Add verification that all in plan_list are plans
        for f in file_list:
            plan = f.split('\\')[-4]
            section = f.split('\\')[-3]
            tile = f.split('\\')[-2]
            if f.endswith('.feather'):
                df = pd.read_feather(os.path.join(folder,plan,f))
            else:
                df = pd.read_parquet(os.path.join(folder,plan,f),engine='pyarrow')
            if 'index' in df.columns:
                df.set_index('index',inplace=True)
            df['PLAN'] = plan
            df['SECTION'] = section
            df['TILE'] = tile
            df_all.append(df)

    elif division == 'SECTION':
        file_list = list_files(folder) + list_files(folder, extension='.feather')
        file_list = [f.replace('/', '\\') for f in file_list if 'ALL' not in f]

        for f in file_list:
            plan = f.split('\\')[-3]
            section = f.split('\\')[-2]
            if f.endswith('.feather'):
                df = pd.read_feather(os.path.join(folder,plan,f))
            else:
                df = pd.read_parquet(os.path.join(folder,plan,f),engine='pyarrow')
            if 'index' in df.columns:
                df.set_index('index',inplace=True)
            df['PLAN'] = plan
            df['SECTION'] = section
            df_all.append(df)

    else: return pd.DataFrame()

    df_final = pd.concat(df_all).drop_duplicates().reset_index(drop=True)
    return df_final

# Create a log file (made with IA)
def start_logger(name=None):
    # Define the logs directory (relative to your working directory)
    logs_dir = os.path.join(os.getcwd(), "logs")

    # If logs directory doesn't exist, create it
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Format the current timestamp for filename uniqueness/readability
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Compose the log filename with timestamp, session ID
    if name:
        log_filename = f"postprocessing_log_{name}_{timestamp}.log"
    else:
        log_filename = f"postprocessing_log_{timestamp}.log"

    # Create the full path for the log file in the logs directory
    log_path = os.path.join(logs_dir, log_filename)

    # Create a logger instance uniquely for this session
    logger = logging.getLogger(log_filename)
    logger.setLevel(logging.INFO)  # Set log level to capture info and errors

    # File handler: Each session logs to its own file
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # Log format includes timestamp, level, user ID, and message
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)

    # Attach the handler to the logger
    logger.addHandler(file_handler)

    # Don't print logs in console
    logger.propagate = False

    return(logger)