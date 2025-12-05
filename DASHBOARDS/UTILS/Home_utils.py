import logging
import uuid
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import importlib
from pathlib import Path
import os
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

azure_access = importlib.import_module("DASHBOARDS.azure_access")
azure_url = azure_access.azure_url
access_key = azure_access.access_key
blob_service_client = BlobServiceClient(azure_url, credential = access_key)

# Create a log file (made with IA)
def start_session_logger():
    # Define the logs directory (relative to your working directory)
    logs_dir = os.path.join(os.getcwd(), "logs")

    # If logs directory doesn't exist, create it
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Generate a unique session ID using UUID
    session_id = str(uuid.uuid4())

    # Format the current timestamp for filename uniqueness/readability
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Compose the log filename with timestamp, session ID
    log_filename = f"homepage_log_{timestamp}_{session_id}.log"

    # Create the full path for the log file in the logs directory
    log_path = os.path.join(logs_dir, log_filename)

    # Create a logger instance uniquely for this session
    logger = logging.getLogger(session_id)
    logger.setLevel(logging.INFO)  # Set log level to capture info and errors

    # File handler: Each session logs to its own file
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # Log format includes timestamp, level, user ID, and message
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)

    # Attach the handler to the logger
    logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # or lower

    logger.addHandler(console_handler)

    return(logger, log_filename, log_path)

def upload_log_to_blob(log_path, blob_container, blob_name):

    # Get a client for the specific container and blob (file) you want to upload to
    blob_client = blob_service_client.get_blob_client(container=blob_container, blob=blob_name)

    # Open the log file and upload its contents to Azure Blob
    with open(log_path, "rb") as data:
        # 'overwrite=True' allows replacing existing files with the same name
        blob_client.upload_blob(data, overwrite=True)
    return

def get_logs_from_blob(blob_container,n=10):
    # Connect to azure container
    container_client = blob_service_client.get_container_client(blob_container)
    # List all blobs in the container that look like log files
    blobs = list(container_client.list_blobs(name_starts_with="sessionlog_"))
    # Sort blobs by last modified time, descending
    blobs_sorted = sorted(blobs, key=lambda x: x.last_modified, reverse=True)
    # Take the last N blobs
    recent_blobs = blobs_sorted[:n]
    return recent_blobs  # Each blob has a .name attribute

def download_blob_to_bytes(blob_container,blob_name):
    blob_client = blob_service_client.get_blob_client(container=blob_container, blob=blob_name)
    return(blob_client.download_blob().readall())