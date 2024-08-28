Documentation for setup.ps1 

Purpose
The setup.ps1 script automates the process of setting up a Python environment on a Windows machine. It checks for the existence of Python, installs it if necessary, upgrades pip, and installs required Python packages from a requirements.txt file.

Script Overview
Check for Python Installation
Install Python if Not Present
Upgrade pip
Install Required Python Packages
Detailed Breakdown
1. Check for Python Installation


$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed. Downloading Python..."
Purpose: Checks if Python is installed on the system.
Command: Get-Command python tries to find the Python executable. If it’s not found, the script proceeds to download and install Python.
2. Install Python if Not Present


    # Download Python installer
    $pythonInstaller = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
    $installerPath = "$env:TEMP\python_installer.exe"
    Invoke-WebRequest -Uri $pythonInstaller -OutFile $installerPath

    # Install Python silently
    Start-Process -FilePath $installerPath -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
    Remove-Item $installerPath

    # Check if installation was successful
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "Python installation failed. Please install Python manually."
        exit 1
    }
}
Download Python Installer: Downloads the Python installer from the official Python website.
Install Python Silently: Executes the installer with silent install options to avoid user interaction.
/quiet – Installs Python without user prompts.
InstallAllUsers=1 – Installs Python for all users.
PrependPath=1 – Adds Python to the system PATH.
Verify Installation: Checks if Python was successfully installed. If not, the script outputs an error message and exits.
3. Upgrade pip


# Upgrade pip to the latest version
Write-Host "Upgrading pip..."
python -m ensurepip
python -m pip install --upgrade pip
Purpose: Upgrades pip to the latest version to ensure compatibility with the latest packages.
Commands:
python -m ensurepip – Ensures that pip is installed.
python -m pip install --upgrade pip – Upgrades pip to the latest version.
4. Install Required Python Packages


# Get the directory of the current script
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition
$requirementsPath = Join-Path -Path $scriptDirectory -ChildPath "requirements.txt"

# Install required Python packages
Write-Host "Installing required Python packages..."
python -m pip install -r $requirementsPath --user
Get Script Directory: Determines the directory where the script is located.
Path to requirements.txt: Constructs the path to the requirements.txt file, which should be in the same directory as the script.
Install Packages: Uses pip to install the packages listed in requirements.txt:
--user – Installs packages for the current user, avoiding system-wide changes.
Error Handling
If Python is not found after installation, the script will exit with an error message.
If the requirements.txt file is missing or cannot be accessed, pip will fail to install the required packages, though this is not explicitly handled in the script.
Usage
Place setup.ps1 in the root directory of your project where requirements.txt is also located.
Run the script in a  session with administrative privileges to ensure it can install Python if necessary.


.\setup.ps1
This script will set up your Python environment and ensure that all necessary Python packages are installed, preparing the system for further development or execution of Python scripts.