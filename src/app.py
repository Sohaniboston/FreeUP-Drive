import streamlit as st
from pathlib import Path
from datetime import datetime, date
from drive_client import get_drive_service, list_files_generator, download_file
from utils import human_size, ensure_dirs, init_logging, write_manifest_entry
import pandas as pd
import psutil
import os
from typing import List

st.set_page_config(page_title="FreeUP Drive Backup", layout="wide")

ensure_dirs()
logger = init_logging()

# Persist Drive service between reruns so Scan works after initial auth
if 'service' not in st.session_state:
    st.session_state['service'] = None

st.title("FreeUP Drive - Google Drive Backup Utility")

with st.sidebar:
    st.header("Authentication")
    auth_status = st.empty()
    service = st.session_state.get('service')
    account_label = st.text_input("Account Label (used in folder naming)", value="primary")
    if st.button("Authenticate with Google"):
        try:
            service = get_drive_service()
            st.session_state['service'] = service
            auth_status.success("Authenticated")
        except Exception as e:
            auth_status.error(f"Auth failed: {e}")
    elif service is not None:
        auth_status.info("Already authenticated")

    st.header("Filters")
    min_size_mb = st.number_input("Min Size (MB)", min_value=0, value=50, help="List only files >= this size")
    name_contains = st.text_input("Name contains (substring)", value="")
    col_dates = st.columns(2)
    with col_dates[0]:
        modified_after = st.date_input("Modified After", value=None)
    with col_dates[1]:
        modified_before = st.date_input("Modified Before", value=None)
    mime_preset = st.multiselect("Mime Groups", ["images", "videos", "documents", "archives", "other"], default=[])
    chunk_size_mb = st.slider("Download Chunk Size (MB)", min_value=1, max_value=64, value=8, help="Adjust if you need smaller memory footprint or faster throughput")
    enable_parallel = st.checkbox("Parallel Downloads", value=True, help="Download multiple files concurrently")
    max_workers = st.slider("Max Parallel Workers", min_value=1, max_value=8, value=4) if enable_parallel else 1
    compute_sha256 = st.checkbox("Compute SHA256 after download", value=True, help="Slower; ensures integrity when md5 missing")

    st.header("Destination")
    base_dest = st.text_input("Base Download Folder", value=str(Path.cwd() / "downloads"))
    dest = str(Path(base_dest) / account_label)
    st.caption(f"Full destination path: {dest}")
    # Free space check
    try:
        usage = psutil.disk_usage(dest if Path(dest).exists() else base_dest)
        st.write(f"Free space: {human_size(usage.free)} / Total: {human_size(usage.total)}")
    except Exception:
        st.write("Free space: (unavailable)")
    start_scan = st.button("Scan Drive")

if 'inventory' not in st.session_state:
    st.session_state['inventory'] = []

if start_scan:
    service = st.session_state.get('service')
    if not service:
        st.warning("Authenticate first (or click the Auth button again if token expired)")
    else:
        # Validate date range (user might have chosen After later than Before)
        if modified_after and modified_before and modified_after > modified_before:
            st.error("'Modified After' date cannot be later than 'Modified Before' date. Adjust the range and try again.")
        else:
            st.info("Scanning... this may take a while for large drives")
        # Map mime groups to mime types
        mime_map = {
            'images': ['image/jpeg','image/png','image/gif','image/webp'],
            'videos': ['video/mp4','video/quicktime','video/x-matroska'],
            'documents': ['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/msword'],
            'archives': ['application/zip','application/x-tar','application/x-7z-compressed','application/x-rar-compressed'],
            'other': []
        }
        selected_mime_types: List[str] = []
        for grp in mime_preset:
            selected_mime_types.extend(mime_map.get(grp, []))
        # Date conversions to RFC3339 (UTC midnight assumptions)
        def to_rfc3339(d: date | None, end=False):
            if not d:
                return None
            if end:
                return datetime(d.year, d.month, d.day, 23, 59, 59).isoformat() + 'Z'
            return datetime(d.year, d.month, d.day, 0, 0, 0).isoformat() + 'Z'
        after_rfc = to_rfc3339(modified_after) if modified_after else None
        before_rfc = to_rfc3339(modified_before, end=True) if modified_before else None
        if modified_after and modified_before and modified_after > modified_before:
            pass  # already reported error
        else:
            try:
                files_data = []
                for f in list_files_generator(
                    service,
                    min_size=min_size_mb*1024*1024,
                    mime_types=selected_mime_types if selected_mime_types else None,
                    modified_after=after_rfc,
                    modified_before=before_rfc,
                    name_contains=name_contains if name_contains else None,
                ):
                    files_data.append(f)
                st.session_state['inventory'] = files_data
                if len(files_data) == 0:
                    st.warning("No files matched the filters. Try lowering size, clearing date range, or removing mime filters.")
            except Exception as e:
                # Surface Drive API error details succinctly
                import traceback
                st.error(f"Drive query failed: {e}")
                with st.expander("Show traceback"):
                    st.code(traceback.format_exc())

inventory = st.session_state.get('inventory', [])

if inventory:
    df = pd.DataFrame(inventory)
    df['size_h'] = df['size'].apply(human_size)
    st.subheader(f"Inventory ({len(df)} files)")
    with st.expander("Preview DataFrame"):
        st.dataframe(df[['name','size_h','mimeType','modifiedTime','md5']])
    selected = st.multiselect("Select files to backup", df['name'] + ' | ' + df['id'])
    download_btn = st.button("Download Selected")
    if download_btn:
        Path(dest).mkdir(parents=True, exist_ok=True)
        manifest_path = Path("manifests") / f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        chunk_size_bytes = chunk_size_mb * 1024 * 1024
        progress_container = st.container()
        overall_bar = progress_container.progress(0, text="Overall Progress")
        to_download = [row for _, row in df.iterrows() if (row['name'] + ' | ' + row['id']) in selected]
        total = len(to_download)
        if total == 0:
            st.warning("No files selected")
        else:
            if enable_parallel and total > 1:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                file_progress = {}
                progress_bars = {}
                lock = st.session_state.get('_thread_lock')
                import threading
                if lock is None:
                    lock = threading.Lock()
                    st.session_state['_thread_lock'] = lock
                def task(row):
                    bar = progress_container.progress(0, text=f"{row['name']} 0%")
                    progress_bars[row['id']] = bar
                    def _cb(p):
                        with lock:
                            bar.progress(int(p*100), text=f"{row['name']} {int(p*100)}%")
                    download_file(
                        service,
                        row['id'],
                        Path(dest) / row['name'],
                        logger=logger,
                        manifest_path=manifest_path,
                        meta=row.to_dict(),
                        chunk_size=chunk_size_bytes,
                        progress_cb=_cb,
                        compute_sha256=compute_sha256,
                    )
                completed = 0
                with ThreadPoolExecutor(max_workers=max_workers) as ex:
                    futures = [ex.submit(task, row) for row in to_download]
                    for f in as_completed(futures):
                        completed += 1
                        overall_bar.progress(int(completed/total*100), text=f"Overall {completed}/{total}")
                st.success("Download complete")
            else:
                for idx, row in enumerate(to_download, start=1):
                    file_bar = progress_container.progress(0, text=f"{row['name']} 0%")
                    def _cb(p, r=row, bar=file_bar):
                        bar.progress(int(p*100), text=f"{r['name']} {int(p*100)}%")
                    download_file(
                        service,
                        row['id'],
                        Path(dest) / row['name'],
                        logger=logger,
                        manifest_path=manifest_path,
                        meta=row.to_dict(),
                        chunk_size=chunk_size_bytes,
                        progress_cb=_cb,
                        compute_sha256=compute_sha256,
                    )
                    overall_bar.progress(int(idx/total*100), text=f"Overall {idx}/{total}")
                st.success("Download complete")
