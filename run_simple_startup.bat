@echo off
REM Minimal launcher for FreeUP Drive
REM Usage: double-click or run from cmd

REM Change to repo root (folder containing this script)
cd /d "%~dp0"

REM Activate conda environment
CALL conda activate freeup_drive || (
  echo [ERROR] Could not activate conda environment 'freeup_drive'.
  echo Make sure Conda is installed and the env exists: conda env list
  exit /b 1
)

REM Launch Streamlit app
streamlit run src/app.py %*
