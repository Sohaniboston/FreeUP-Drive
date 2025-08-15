# Google Drive API Cheat Sheet (<=4 pages target)
Version: 2025-08-14

## 1. Core Concept (ELI5)
Drive API = A mailbox to ask Google: list, read, create, move, share, or delete files. Each permission set is a scope (key). Use the smallest key.

## 2. Scope (Permission) Tiers
| Tier | Scope(s) | Power | Typical Use |
|------|----------|-------|-------------|
| Metadata Read | drive.metadata.readonly | View names, sizes (some), timestamps | Inventory dashboards |
| Full Read | drive.readonly | Metadata + download content | Backup / audit |
| App File Read/Write | drive.file | CRUD only on app-created/opened files | Focused editors, export tools |
| Full Read/Write | drive | CRUD + share + trash everything user can access | Migration, sync (high risk) |
| App Hidden Storage | drive.appdata | Private config blobs | Tokens, settings |

Addons: `drive.photos.readonly` (photos), Shared Drives allowed by adding parameters.

## 3. When to Pick Which
| Need | Recommended Scope |
|------|-------------------|
| List large files only | drive.metadata.readonly |
| Download backups | drive.readonly |
| Upload new file (app-owned) | drive.file |
| Edit existing arbitrary files | drive |
| Store hidden state | drive.appdata |

## 4. Key Operations & HTTP Mapping
| Action | Method + Endpoint | Notes |
|--------|-------------------|-------|
| List files | GET /drive/v3/files | Use `q`, `pageSize`, `fields` |
| Get metadata | GET /drive/v3/files/{id} | Add `fields=` narrow projection |
| Download | GET /drive/v3/files/{id}?alt=media | Binary content |
| Create upload | POST /upload/drive/v3/files?uploadType=multipart | Metadata + media |
| Update metadata | PATCH /drive/v3/files/{id} | JSON body partial |
| Move (change parent) | PATCH /drive/v3/files/{id}?addParents=&removeParents= | Provide parent IDs |
| Delete | DELETE /drive/v3/files/{id} | Moves to trash if not permanent |
| Trash / restore | PATCH /drive/v3/files/{id} ("trashed": true/false) | |
| Revisions list | GET /drive/v3/files/{id}/revisions | Requires read scope |
| Permissions add | POST /drive/v3/files/{id}/permissions | drive / drive.file |

## 5. Common Query Filters (`q=`)
Combine with `and`; wrap strings in single quotes.
- `name contains 'report'`
- `mimeType = 'application/pdf'`
- `mimeType contains 'image/'`
- `modifiedTime > '2025-01-01T00:00:00Z'`
- `size > 104857600` ( >100MB )
- `trashed = false`
Example: `trashed=false and size > 104857600 and name contains 'backup'`

## 6. Fields (Partial Response) Examples
- Basic: `files(id,name,size,mimeType,modifiedTime,md5Checksum)`
- With nextPageToken: `nextPageToken, files(id,name,parents)`
Use only what you need to cut payload size.

## 7. Rate Limits & Resilience
| Issue | Mitigation |
|-------|------------|
| 429 / quota exceeded | Exponential backoff (2^n base) |
| 403 insufficient permissions | Re-check scope / sharing |
| 401 expired token | Refresh token or re-auth |
| Timeouts | Smaller pageSize or partial fields |

Retry pattern (pseudo):
```
for attempt in range(5):
  try: call(); break
  except Transient: sleep(backoff(attempt))
```

## 8. Integrity & Backup Tips
- Capture `id`, `name`, `size`, `modifiedTime`, `md5Checksum`.
- If `md5Checksum` missing (Google Docs), export or snapshot to PDF first if needed.
- Compute local SHA256 after download for long-term verification.
- Store manifest as JSONL for streaming writes.

## 9. Security Least Privilege Ladder
1. Start: `drive.metadata.readonly`
2. Need content? upgrade -> `drive.readonly`
3. Need to create own files? add/replace -> `drive.file`
4. Absolutely must touch arbitrary existing files? escalate -> `drive` (document reason).

## 10. Shared Drives (Team Drives)
Add parameters: `supportsAllDrives=true&includeItemsFromAllDrives=true`.
Filter inside shared drive: `'<driveId>' in parents` (list root first to get driveId or use drives().list()).

## 11. Sample Minimal Python (Read-Only Listing)
```
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
service = build('drive','v3',credentials=creds)
resp = service.files().list(q="trashed=false", pageSize=1000,
    fields="nextPageToken, files(id,name,size,mimeType,modifiedTime,md5Checksum)").execute()
for f in resp.get('files', []):
    print(f['name'], f.get('size'))
```

## 12. Permissions Basics
| Role | Effect |
|------|--------|
| reader | View & download |
| commenter | View + comment (Google Docs types) |
| writer | Edit content |
| organizer | Manage within shared drives |
| owner | Full control & transfer |

Add permission (JSON body): `{"type":"user","role":"reader","emailAddress":"user@example.com"}`

## 13. Deletion Safety
- Use trash first (`{"trashed": true}`) not DELETE unless confident.
- Permanently deleting bypasses recovery.

## 14. App Data Folder
- Special hidden storage: set `spaces=appDataFolder` when listing.
- Good for config caches; limited size (~app constraints). Use `drive.appdata` scope.

## 15. Quick Decision Tree
Start listing? -> metadata.readonly
Need file bytes? -> readonly
Need to upload new file? -> file
Need to modify existing arbitrary file? -> full drive
Need config store? -> add appdata

## 16. Glossary
| Term | Meaning |
|------|---------|
| Scope | OAuth permission string |
| Page Token | Cursor for next page listing |
| Manifest | Local log of backed-up file metadata |
| Revision | Historical version of file |
| Parents | Folder IDs containing the file |

## 17. Top 10 Pitfalls
1. Requesting full `drive` scope unnecessarily.
2. Forgetting `trashed=false` filter -> cluttered results.
3. Not using partial `fields` -> slow responses.
4. Ignoring exponential backoff -> quota hits.
5. Treating Google Docs like binary files (no size/md5).
6. Overwriting local files with same name ID collisions.
7. Missing shared drive flags -> incomplete listings.
8. Storing tokens in version control.
9. Skipping manifest integrity data.
10. Not validating chunked download completion.

## 18. Minimal Risk Checklist (Before Deploy)
- [ ] Narrowest scope chosen
- [ ] Token stored outside repo
- [ ] Backoff & retry implemented
- [ ] Manifest includes checksum/time
- [ ] Partial responses used
- [ ] Logging redacts sensitive data

---
End of Cheat Sheet.
