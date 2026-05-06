# Quick activation script for GDAL environment
# Usage: .\activate_gdal_env.ps1

$env:PATH = "C:\Users\ashut\miniconda3\Scripts;C:\Users\ashut\miniconda3;$env:PATH"

Write-Output "================================"
Write-Output "GDAL Environment Activation"
Write-Output "================================"
Write-Output ""
Write-Output "Current conda version: $(conda --version)"
Write-Output ""
Write-Output "Available environments:"
conda env list
Write-Output ""
Write-Output "To activate gdal_env, run:"
Write-Output "  conda activate gdal_env"
Write-Output ""
Write-Output "Then verify GDAL:"
Write-Output "  python -c `"from osgeo import gdal; print('GDAL version:', gdal.__version__)`""
