@echo off
REM One-click start for the Bridge Simulator with Web ECDIS
REM Assumes you created a conda env named gdal_env with required packages.

SETLOCAL ENABLEDELAYEDEXPANSION

REM Optional: set environment variable to enable demo circular motion
REM SET ECDIS_DEMO=1

REM Activate environment and run
call conda run -n gdal_env python -m bridge_sim.main

ENDLOCAL
