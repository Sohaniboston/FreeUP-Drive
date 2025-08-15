from __future__ import annotations
from pathlib import Path
from typing import Dict, Generator, Optional, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
import io
from tenacity import retry, wait_exponential, stop_after_attempt
import json
import hashlib

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_FILE = Path("secrets/credentials.json")
TOKEN_FILE = Path("secrets/token.json")


def get_drive_service():
    creds: Optional[Credentials] = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    return service


def list_files_generator(
    service,
    page_size: int = 1000,
    min_size: int = 0,
    mime_types: Optional[List[str]] = None,
    modified_after: Optional[str] = None,
    modified_before: Optional[str] = None,
    name_contains: Optional[str] = None,
) -> Generator[Dict, None, None]:
    """Generate file metadata records from Drive according to filters.

    Args:
        service: Authenticated Drive service.
        page_size: API page size (max 1000 for Drive).
        min_size: Minimum size in bytes (excludes Google Docs lacking size when set).
        mime_types: List of exact mime types to include (OR logic). If None, all types.
        modified_after: RFC3339 timestamp inclusive lower bound.
        modified_before: RFC3339 timestamp inclusive upper bound.
        name_contains: Substring for name search (case-insensitive server-side).
    """
    page_token = None
    q_parts = ["trashed = false", "mimeType != 'application/vnd.google-apps.folder'"]
    # NOTE: The Drive v3 search syntax does NOT support filtering by 'size' server-side.
    # (Using size > N causes a 400 Invalid Value error). We therefore apply min_size
    # client-side after retrieval. Keeping this comment to prevent regressions.
    if mime_types:
        or_clause = " or ".join([f"mimeType = '{mt}'" for mt in mime_types])
        q_parts.append(f"({or_clause})")
    if modified_after:
        q_parts.append(f"modifiedTime >= '{modified_after}'")
    if modified_before:
        q_parts.append(f"modifiedTime <= '{modified_before}'")
    if name_contains:
        safe_term = name_contains.replace("'", "\'")
        q_parts.append(f"name contains '{safe_term}'")
    query = " and ".join(q_parts)
    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, size, mimeType, modifiedTime, md5Checksum)",
            pageToken=page_token,
            pageSize=page_size,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        for f in response.get('files', []):
            size = int(f.get('size') or 0)
            if min_size > 0 and size < min_size:
                continue  # client-side size filter
            yield {
                'id': f['id'],
                'name': f['name'],
                'size': size,
                'mimeType': f.get('mimeType'),
                'modifiedTime': f.get('modifiedTime'),
                'md5': f.get('md5Checksum')
            }
        page_token = response.get('nextPageToken')
        if not page_token:
            break


@retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(5))
def download_file(
    service,
    file_id: str,
    dest_path: Path,
    logger=None,
    manifest_path: Path | None = None,
    meta: Dict | None = None,
    chunk_size: int = 8 * 1024 * 1024,
    progress_cb=None,
    compute_sha256: bool = False,
):
    """Download a single Drive file with progress callback and manifest append.

    Args:
        service: Drive service
        file_id: File ID
        dest_path: Local output path
        logger: Optional logger
        manifest_path: JSONL manifest path
        meta: Metadata dict to enrich manifest
        chunk_size: Download chunk size in bytes
        progress_cb: Callable(float 0-1) for UI progress updates
    """
    request = service.files().get_media(fileId=file_id)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request, chunksize=chunk_size)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            pct = float(status.progress())
            if progress_cb:
                progress_cb(pct)
            if logger:
                logger.info(f"Downloading {dest_path.name}: {int(pct*100)}%")
    sha256_hash = None
    if compute_sha256:
        # Compute SHA256 after download
        h = hashlib.sha256()
        with open(dest_path, 'rb') as rf:
            for chunk in iter(lambda: rf.read(1024 * 1024), b''):
                h.update(chunk)
        sha256_hash = h.hexdigest()
    if logger:
        logger.info(f"Downloaded {dest_path}" + (f" sha256={sha256_hash}" if sha256_hash else ""))
    if manifest_path:
        from datetime import datetime as _dt
        entry = meta.copy() if meta else {'id': file_id, 'name': dest_path.name}
        entry['localPath'] = str(dest_path)
        entry['downloadedAt'] = _dt.utcnow().isoformat() + 'Z'
        if sha256_hash:
            entry['sha256'] = sha256_hash
        entry_out = json.dumps(entry)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, 'a', encoding='utf-8') as mf:
            mf.write(entry_out + "\n")
