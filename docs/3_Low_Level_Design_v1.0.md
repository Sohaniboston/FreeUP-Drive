# Low Level Design (LLD)
Project: Google Drive Auto Backup Utility  
Version: 1.0  
Date: 2025-08-14

## 1. Module Breakdown
| Module | Path | Responsibilities |
|--------|------|------------------|
| UI | `src/app.py` | Render controls, manage session state, orchestrate workflow |
| Drive Client | `src/drive_client.py` | OAuth auth, file listing, file download w/ retry |
| Utils | `src/utils.py` | Logging, directory creation, formatting, manifest writes |

## 2. Detailed Function Specs
### 2.1 `get_drive_service()`
- Inputs: None (reads credentials/token paths)
- Outputs: Authenticated Drive API service object.
- Errors: Raises on missing credentials file or OAuth failure.
- Steps: Load token -> refresh or initiate flow -> persist token -> build service.

### 2.2 `list_files_generator(service, page_size=1000, min_size=0)`
- Inputs: service, page_size, min_size bytes.
- Output: Yields dict per file (id, name, size, mimeType, modifiedTime, md5).
- Logic: Construct query; paginate using nextPageToken until exhaustion.

### 2.3 `download_file(service, file_id, dest_path, logger, manifest_path, meta)`
- Inputs: service, file id, destination path, optional logger, manifest path, metadata.
- Output: None (side effect: writes file, manifest line).
- Logic: Create Get Media request -> loop on `downloader.next_chunk()` until done -> log progress -> append metadata.
- Retry: 5 attempts w/ exponential backoff using tenacity decorator.

### 2.4 `ensure_dirs()`
- Creates `logs/`, `manifests/`, `downloads/`, `secrets/` if absent.

### 2.5 `init_logging()`
- Creates timestamped log file; configures root logger handlers.

### 2.6 `human_size(num)`
- Converts integer bytes to human readable string.

### 2.7 `write_manifest_entry(path, entry)`
- Appends JSON line to manifest file.

## 3. Data Structures
Python dictionaries for lightweight records. Example inventory item:  
```
{
  "id": "1AbcDEF...",
  "name": "video.mp4",
  "size": 104857600,
  "mimeType": "video/mp4",
  "modifiedTime": "2025-08-13T10:05:22.123Z",
  "md5": "d41d8cd98f00b204e9800998ecf8427e"
}
```

Manifest line (JSONL):
```
{"id":"1AbcDEF","name":"video.mp4","size":104857600,"mimeType":"video/mp4","modifiedTime":"2025-08-13T10:05:22.123Z","md5":"..."}
```

## 4. Session State Keys (Streamlit)
| Key | Type | Purpose |
|-----|------|---------|
| `inventory` | list[dict] | Cached file list post-scan |

## 5. Error Handling
- Authentication errors caught and shown via `st.error()`.
- Download retries escalate exception after max attempts; UI logs error.

## 6. Logging Conventions
Format: `timestamp level message`  
Sample: `2025-08-14 12:00:01,234 INFO Downloading video.mp4: 60%`

## 7. Performance Considerations
- Streaming listing prevents huge in-memory object creation per page.
- Potential optimization: yield to UI incrementally for progressive rendering (future improvement using st.dataframe updates).

## 8. Security Details
- Secrets folder outside version control (gitignore to be added).
- Principle of least privilege via read-only scope.

## 9. Extension Points
- Add parameters: mime types, date range -> extend query builder.
- Integrity: compute SHA256 after download if md5Checksum missing.
- Parallelization: thread pool for independent downloads (bounded by I/O).

## 10. Sequence Example (Download Path)
1. User selects files.
2. For each file metadata row -> call `download_file`.
3. Function streams chunks until completion.
4. Append manifest line; proceed to next.

## 11. Testing Strategy (Initial)
- Unit test `human_size` edge cases.
- Mock Drive service for list & download to ensure retry decorator called.
- Smoke test launching Streamlit app script import (no runtime errors).

## 12. Open Items
- Add proper progress bars in UI (Streamlit progress component) v1.1.
- Expand manifest fields (sha256, localPath, downloadedAt). v1.1.
