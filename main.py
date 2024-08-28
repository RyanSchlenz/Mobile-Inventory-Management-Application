import os
import subprocess
import time
from credentials import project_config

# Load configuration from credentials.py
scripts = project_config['scripts']
csv_files = project_config['csv_files']

# Function to get the full path of a file in the same directory as the script
def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

# Function to run a script
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

# Function to check if required CSV files exist
def check_csv_files(files, retries=3, delay=2):
    for attempt in range(retries):
        missing_files = [get_file_path(file) for file in files if not os.path.isfile(get_file_path(file))]
        if not missing_files:
            return True
        print(f"Attempt {attempt + 1}: Missing files: {', '.join(missing_files)}")
        time.sleep(delay)
    return False

# Function to delete created CSV files
def delete_csv_files(files):
    for file in files:
        file_path = get_file_path(file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

# Function to run all scripts and check CSV file existence
def run_all_scripts():
    retries = 3
    while retries > 0:
        # Run each main script in order
        success = True
        
        # Run the main scripts
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

if __name__ == "__main__":
    run_all_scripts()
