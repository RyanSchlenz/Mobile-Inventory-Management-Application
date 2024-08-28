# Check if Python is installed
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed. Downloading Python..."
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

# Upgrade pip to the latest version
Write-Host "Upgrading pip..."
python -m ensurepip
python -m pip install --upgrade pip

# Get the directory of the current script
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition
$requirementsPath = Join-Path -Path $scriptDirectory -ChildPath "requirements.txt"

# Install required Python packages
Write-Host "Installing required Python packages..."
python -m pip install -r $requirementsPath --user

