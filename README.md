# FreeUP Drive - Google Drive Backup Utility

Version: 0.2.0

A Streamlit-based utility to authenticate with Google Drive, discover large or filtered files, and download them to organized local storage with logging, manifesting, progress bars, and configurable performance parameters.

## Features (MVP v1.0)
- OAuth2 desktop login (read-only scope)
- Filters: size threshold, mime groups, specific mime types, name contains, modified date range
- Inventory listing with expandable preview and human-readable sizes
- Account label -> destination subfolder naming
- Free disk space display for target volume
- Resumable multi-part downloads with per-file and overall progress bars
- Configurable chunk size (1–64 MB) for performance tuning
- JSONL manifest with metadata + local path + timestamp
- Structured logging per run with progress lines
- Error handling & retry (exponential backoff)

## Planned (Post-MVP)
- Incremental diff & duplicate detection (v1.1+)
- Parallel downloads (v1.1)
- Windows Task Scheduler helper script (initial draft coming) & optional email summaries
- Optional encryption at rest (v2.0)
- Multi-account aggregation UI (v2.0)
- Enhanced integrity hashing (SHA256) (v1.2)

## Quick Start
Install deps:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Create Google Cloud project + OAuth Client (Desktop) and download credentials.json into `secrets/credentials.json`.

Run app:
```
streamlit run src/app.py
```

## Logs & Output
- Logs: `logs/run_YYYYMMDD_HHMMSS.log`
- Manifest: `manifests/manifest_YYYYMMDD_HHMMSS.json`
- Downloads: user-selected destination path

## Google Cloud & OAuth Setup (Step-by-Step)
1. Sign in to https://console.cloud.google.com/ (create an account if needed).
2. Click Select Project -> New Project. Enter a name (e.g., FreeUP-Drive-Backup) and create.
3. With the project selected, open Navigation Menu -> APIs & Services -> Library.
4. Search for "Google Drive API" and click Enable.
5. Go to APIs & Services -> OAuth consent screen:
	- User Type: External (unless you have a Workspace org) -> Create.
	- App name: FreeUP Drive Backup (or your preference).
	- User support email + Developer contact email: your email.
	- (Optional) Add logo/scopes later; Save and Continue until Summary -> Back to Dashboard.
6. Go to APIs & Services -> Credentials -> Create Credentials -> OAuth client ID.
	- Application type: Desktop app.
	- Name: FreeUP Drive Desktop.
	- Create -> Download the JSON (client_secret_*.json).
7. Create folder `secrets/` in project root if not present.
8. Rename downloaded file to `credentials.json` and place into `secrets/credentials.json`.
9. (Optional) Restrict OAuth but generally not required for desktop.
10. Run the app: `streamlit run src/app.py` (activate venv first). A browser will open for consent.
11. After approval, `secrets/token.json` is created (stores refresh token). Keep this private.
12. If you rotate credentials, delete `secrets/token.json` to force re-auth.

## Windows Task Scheduler (Preview Snippet)
Create a `.bat` file (e.g., `run_backup.bat`):
```
@echo off
call .venv\Scripts\activate
streamlit run src\app.py --server.headless true
```
Then schedule via Task Scheduler -> Create Basic Task -> Trigger as desired -> Action: Start a program -> Program/script: path to the batch file.

## License
MIT License (see LICENSE file)
