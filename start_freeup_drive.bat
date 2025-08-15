@echo off
REM FreeUP Drive startup script (conda) - create env if missing, install deps, run app.
setlocal

REM --- Configuration ---
set ENV_NAME=freeup_drive
set PY_VERSION=3.12
set REQUIREMENTS=requirements.txt
set APP_ENTRY=src\app.py
set GCP_URL=https://console.cloud.google.com/
set GCP_DRIVE_API_URL=https://console.cloud.google.com/apis/library/drive.googleapis.com
REM Marker (not used in simplified version) left for future optimization
set BOOTSTRAP_MARKER=.pip_installed.txt

echo [INFO] Checking for conda...
where conda >nul 2>&1 || (echo [ERROR] conda not found on PATH & exit /b 1)

REM --- Try activating environment; if fails, create then activate ---
call conda activate %ENV_NAME% >nul 2>&1
if errorlevel 1 (
    echo [INFO] Environment '%ENV_NAME%' not found. Creating...
    conda create -y -n %ENV_NAME% python=%PY_VERSION% pip || (echo [ERROR] Env creation failed & exit /b 1)
    call conda activate %ENV_NAME% || (echo [ERROR] Activation failed after creation & exit /b 1)
) else (
    echo [INFO] Using existing environment '%ENV_NAME%'.
)

echo [INFO] Verifying Python interpreter inside environment:
python -c "import sys; print('Interpreter:', sys.executable); print('Version:', sys.version.split()[0])" || (echo [ERROR] Python check failed & exit /b 1)

REM --- Parse optional flags ---
set FORCE=0
if /I "%1"=="--force" set FORCE=1

REM --- Conditional dependency install (simplified to avoid batch quoting issues) ---
if exist %REQUIREMENTS% (
    if %FORCE%==1 (
        echo [INFO] Force mode: upgrading pip and fully syncing requirements.
        python -m pip install --upgrade pip >nul 2>&1
        pip install -r %REQUIREMENTS% || (echo [ERROR] pip install failed & exit /b 1)
    ) else (
        echo [INFO] Installing only missing or version-mismatched packages (no eager upgrades)...
        REM Pip default strategy only updates when needed; pass --upgrade-strategy only-if-needed explicitly.
        pip install -r %REQUIREMENTS% --upgrade-strategy only-if-needed || (echo [ERROR] pip install failed & exit /b 1)
    )
) else (
    echo [WARN] %REQUIREMENTS% not found. Skipping dependency install.
)

REM --- Ensure directory structure ---
for %%D in (logs manifests downloads secrets) do if not exist %%D mkdir %%D

REM --- Open Google Cloud pages only first time (no marker) ---
if not exist secrets\credentials.json (
    echo [INFO] Opening Google Cloud Console pages for initial setup...
    start "" %GCP_URL%
    start "" %GCP_DRIVE_API_URL%
    echo.
    echo =============================================================
    echo  Create OAuth Desktop credentials and place as secrets\credentials.json
    echo =============================================================
    echo.
    echo Press any key AFTER placing credentials.json to continue.
    pause >nul
) else (
    echo [INFO] credentials.json present.
)

echo [INFO] Launching FreeUP Drive App...
streamlit run %APP_ENTRY%

endlocal
