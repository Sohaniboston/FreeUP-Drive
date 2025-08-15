# Google Cloud & OAuth Setup Guide

This guide walks through creating and configuring a Google Cloud project for FreeUP Drive.

## 1. Create / Select Google Account
Use or create a Google account with access to the target Drive data.

## 2. Open Cloud Console
https://console.cloud.google.com/

## 3. Create Project
1. Click project selector (top-left) -> New Project.
2. Name: FreeUP-Drive-Backup (or preferred).
3. Create. Wait until project is ready.

## 4. Enable Drive API
1. Navigation Menu -> APIs & Services -> Library.
2. Search "Google Drive API".
3. Click -> Enable.

## 5. Configure OAuth Consent Screen
1. APIs & Services -> OAuth consent screen.
2. User Type: External (unless Workspace internal) -> Create.
3. App name: FreeUP Drive Backup.
4. User support email, Developer contact email: your email.
5. Scopes: Add scope -> Select drive.readonly (or leave basic if not visible yet). (The application only needs read-only scope.)
6. Test users: Add your email (required before publishing for External apps in testing mode).
7. Save & Continue until Summary -> Back to Dashboard.

## 6. Create OAuth Client Credentials
1. APIs & Services -> Credentials.
2. Click Create Credentials -> OAuth client ID.
3. Application type: Desktop app.
4. Name: FreeUP Desktop Client.
5. Create -> Download JSON.

## 7. Place Credentials
1. In your project directory, create `secrets/` if missing.
2. Rename downloaded file to `credentials.json`.
3. Place it in `secrets/credentials.json`.
4. Ensure `.gitignore` includes `secrets/` (already configured).

## 8. Run Application
1. Create & activate virtual environment:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Launch app:
```
streamlit run src/app.py
```
3. Browser window prompts for Google login & consent.

## 9. Token Storage
- After first auth, `secrets/token.json` is generated (refresh token + credentials info).
- Safe to keep locally; DO NOT commit.
- Delete this file to force a fresh OAuth flow if needed.

## 10. Troubleshooting
| Issue | Cause | Resolution |
|-------|-------|-----------|
| Invalid client error | Wrong or malformed credentials.json | Re-download credentials; ensure correct file placed. |
| Redirect URI mismatch | Desktop app type not chosen | Re-create OAuth client as Desktop type. |
| Access blocked (unverified app) | App not published | Add your email as Test User on consent screen. |
| 403 insufficient permissions | Wrong scope | Ensure scope set is drive.readonly. Delete token.json & re-auth. |

## 11. Rotating Credentials
- Revoke old in Credentials page.
- Create new OAuth client.
- Replace `credentials.json`, delete `token.json`, relaunch app.

## 12. Optional Hardening
- Limit test users only.
- Publish the app after verification (if sharing widely) to remove test user limit.
- Consider service account (read-only) for automated non-user tasks (future enhancement).

## 13. Next Steps
- Set up Windows Task Scheduler (see README) for periodic invocation.
- Explore upcoming features: incremental diff, parallel optimization tuning.

---
This document can be updated as new features (service accounts, incremental backups) are added.
