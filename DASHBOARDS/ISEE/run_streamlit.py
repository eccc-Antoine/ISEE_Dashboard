import subprocess
import sys
import os
from datetime import datetime
import uuid
from pathlib import Path
import threading
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import DASHBOARDS.UTILS.Home_utils as UTILS

# Generate a unique log file for this run (or use a fixed name for simplicity)
logs_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_dir, exist_ok=True)

session_id = str(uuid.uuid4())
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
runner_log_filename = f"streamlit_runnerlog_{timestamp}_{session_id}.log"
runner_log_path = os.path.join(logs_dir, runner_log_filename)

upload_interval = 10

def periodic_upload(stop_event):
    while not stop_event.is_set():
        try:
            if os.path.exists(runner_log_path):
                UTILS.upload_log_to_blob(runner_log_path, 'session-logs', runner_log_filename)
                print("Uploaded runner log to blob.")
            else:
                print("Log file does not exist yet, skipping upload.")
        except Exception as e:
            print(f"Failed to upload log: {e}")
        stop_event.wait(upload_interval)

def run_streamlit():
    with open(runner_log_path, "w", encoding="utf-8") as logfile:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "DASHBOARDS/ISEE/Home_🏠.py", "--server.port=443", "--server.address=0.0.0.0", "--logger.level=debug"],
            stdout=logfile,
            stderr=subprocess.STDOUT
        )
    return process

if __name__ == "__main__":
    # For graceful shutdown:
    stop_event = threading.Event()
    # Start periodic upload in background
    uploader_thread = threading.Thread(target=periodic_upload, args=(stop_event,), daemon=True)
    uploader_thread.start()
    try:
        process = run_streamlit()
        exit_code = process.wait()
        UTILS.upload_log_to_blob(runner_log_path, 'session-logs', runner_log_filename)
    except Exception as e:
        with open(runner_log_path, "a", encoding="utf-8") as logfile:
            logfile.write(f"\nException occurred in runner: {str(e)}\n")
        UTILS.upload_log_to_blob(runner_log_path, 'session-logs', runner_log_filename)
    finally:
        # Stop the uploader thread
        stop_event.set()
        uploader_thread.join(timeout=5)
        print("Uploader thread stopped.")