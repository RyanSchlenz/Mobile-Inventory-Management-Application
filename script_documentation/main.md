Documentation for main.py

Overview
The main.py script orchestrates the execution of a series of Python scripts and manages CSV files used by these scripts. It ensures that:

Scripts are executed in a specified order.
Required CSV files are checked for existence.
Created CSV files are deleted after a successful run.
Retries are handled if scripts fail or files are missing.

Imports

import os
import subprocess
import time
from credentials import project_config
Constants
scripts: List of script filenames to be executed, loaded from the project_config dictionary in credentials.py.
csv_files: List of CSV filenames to check for existence and to delete after execution. Defaults to an empty list if not specified in project_config.
Functions
get_file_path(filename)
Returns the full path of a file located in the same directory as the script.

Parameters:
filename (str) - Name of the file.
Returns: Full file path (str).


def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)
run_script(script)
Executes a Python script.

Parameters:
script (str) - Name of the script to run.
Returns: True if the script runs successfully, False otherwise.


def run_script(script):
    script_path = get_file_path(script)
    try:
        print(f"Running {script_path}...")
        subprocess.check_call(['python', script_path])
        print(f"Successfully ran {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {script_path}: {e}")
        return False
check_csv_files(files, retries=3, delay=2)
Checks if the specified CSV files exist. Retries if files are missing.

Parameters:
files (list) - List of CSV filenames to check.
retries (int) - Number of retry attempts (default is 3).
delay (int) - Delay between retries in seconds (default is 2).
Returns: True if all files are present, False otherwise.


def check_csv_files(files, retries=3, delay=2):
    for attempt in range(retries):
        missing_files = [get_file_path(file) for file in files if not os.path.isfile(get_file_path(file))]
        if not missing_files:
            return True
        print(f"Attempt {attempt + 1}: Missing files: {', '.join(missing_files)}")
        time.sleep(delay)
    return False
delete_csv_files(files)
Deletes the specified CSV files if they exist.

Parameters:
files (list) - List of CSV filenames to delete.
Returns: None


def delete_csv_files(files):
    for file in files:
        file_path = get_file_path(file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")
run_all_scripts()
Manages the overall script execution and file management process:

Executes each script in the order specified in scripts.
Checks for the presence of all required CSV files.
Deletes CSV files after successful execution and waiting for a specified period.
Handles retries if scripts fail or files are missing.
Parameters: None
Returns: None


def run_all_scripts():
    retries = 3
    while retries > 0:
        # Run each main script in order
        success = True
        for script in scripts:
            if not run_script(script):
                success = False
                break  # Exit if any script fails
        
        # Add a short delay before checking for CSV files
        time.sleep(2)
        
        # Check if all required CSV files exist
        if success and check_csv_files(csv_files):
            print("All scripts ran successfully and all required CSV files are present.")
            
            # Wait 3 minutes before deleting all CSV files
            print("Waiting for 3 minutes before deleting CSV files...")
            time.sleep(180)  # 3 minutes = 180 seconds
            
            # Delete all CSV files created during the script execution
            delete_csv_files(csv_files)
            
            break
        else:
            print("One or more files are missing. Rerunning scripts...")
            retries -= 1
            if retries > 0:
                time.sleep(5)  # Wait before retrying
            else:
                print("Failed after multiple attempts. Please check the scripts and CSV files.")
Main Execution
The script starts by calling run_all_scripts() if it is executed as the main module.



if __name__ == "__main__":
    run_all_scripts()
This script provides a robust framework for executing and managing the lifecycle of multiple scripts and related files, ensuring that all tasks are completed and files are properly handled.