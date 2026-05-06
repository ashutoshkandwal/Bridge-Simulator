# Miniconda Installation Script for Windows PowerShell
# This script downloads Miniconda, installs it, and sets up GDAL environment

Write-Output "======================================"
Write-Output "Miniconda Installation Script"
Write-Output "======================================"

$downloadsPath = "$env:USERPROFILE\Downloads"
$installerName = "Miniconda3-latest-Windows-x86_64.exe"
$installerPath = "$downloadsPath\$installerName"
$installDir = "$env:USERPROFILE\miniconda3"

Write-Output ""
Write-Output "Step 1: Downloading Miniconda3..."
Write-Output "=========================================="

# Download Miniconda
$downloadUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"

try {
    if (Test-Path $installerPath) {
        Write-Output "✓ Installer already exists at: $installerPath"
    } else {
        Write-Output "Downloading from: $downloadUrl"
        Write-Output "Saving to: $installerPath"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Output "✓ Download complete!"
    }
} catch {
    Write-Output "✗ Download failed: $_"
    Write-Output ""
    Write-Output "Please download manually from:"
    Write-Output "  https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    Write-Output ""
    Write-Output "Then save to: $installerPath"
    exit 1
}

Write-Output ""
Write-Output "Step 2: Installing Miniconda3..."
Write-Output "=========================================="
Write-Output "Installation directory: $installDir"
Write-Output "This will take 2-3 minutes..."

# Run installer
if (Test-Path $installerPath) {
    $process = Start-Process -FilePath $installerPath -ArgumentList `
        "/InstallationType=JustMe /AddMinicondaToPath=1 /RegisterPython=0 /S /D=$installDir" `
        -Wait -NoNewWindow
    
    Write-Output "✓ Installation started!"
    Write-Output ""
    Write-Output "Installation will run in the background."
    Write-Output ""
} else {
    Write-Output "✗ Installer not found!"
    exit 1
}

Write-Output "Step 3: Post-Installation..."
Write-Output "=========================================="
Write-Output ""
Write-Output "⚠️  IMPORTANT: You MUST close this PowerShell window completely"
Write-Output "   and open a NEW PowerShell window for conda to work."
Write-Output ""
Write-Output "Then run these commands:"
Write-Output ""
Write-Output "  1. conda --version"
Write-Output "  2. conda create -n gdal_env python=3.10 gdal fiona shapely pyproj -c conda-forge -y"
Write-Output "  3. conda activate gdal_env"
Write-Output "  4. python -c \"from osgeo import gdal; print('GDAL version:', gdal.__version__)\""
Write-Output ""
Write-Output "======================================"
Write-Output "Press any key to continue..."
Write-Output "======================================"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
