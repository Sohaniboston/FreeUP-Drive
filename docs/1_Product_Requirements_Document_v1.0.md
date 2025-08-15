# Product Requirements Document (PRD)
Project: Google Drive Auto Backup Utility  
Version: 1.0  
Date: 2025-08-14

## 1. Executive Summary
A desktop-friendly Streamlit application enabling users to authenticate with Google Drive, discover large/old/targeted files quickly, and download selected items to local or offline storage with resilient, logged, verifiable transfers. Addresses pain of quota management and absence of a lightweight backup workflow.

## 2. Goals & Non-Goals
### 2.1 Goals
- G1: Provide secure OAuth2 authentication (read-only scope) for a single user account.
- G2: Enumerate non-folder Drive files with performant pagination and filtering.
- G3: Allow interactive selection (multi-select) and batch download to chosen destination.
- G4: Ensure reliability via resumable downloads, logging, and retry/backoff.
- G5: Produce manifest capturing metadata & checksums for audit and future incremental runs.
- G6: Offer minimal, intuitive UI enabling first-time completion under 10 minutes.

### 2.2 Non-Goals (MVP)
- NG1: Automatic scheduled recurring backups (guidance only).
- NG2: Deletion or cleanup operations on Google Drive.
- NG3: Multi-user role management.
- NG4: Real-time synchronization or continuous watch.
- NG5: Encryption or compression of downloaded files.

## 3. User Stories & Acceptance Criteria
| ID | User Story | Acceptance Criteria |
|----|------------|--------------------|
| US1 | As a user, I want to authenticate so the app can access my Drive files. | Login button initiates OAuth; on success session holds Drive service; failure shows error. |
| US2 | As a user, I want to filter by minimum size to focus on large files. | Size filter (MB) reduces listed files; entering 0 returns all (subject to API limits). |
| US3 | As a user, I want to view key metadata (name, size, mime, modified date). | Inventory table displays these columns and supports sorting. |
| US4 | As a user, I want to multi-select files to download. | UI offers multi-select referencing file name + ID; chosen set persisted until new scan. |
| US5 | As a user, I want downloads to resume and retry on transient errors. | Interrupted network triggers retry attempts (<=5) with exponential backoff. |
| US6 | As a user, I want a manifest for integrity and audit. | Each downloaded file produces a JSONL line containing id, name, size, md5, modifiedTime. |
| US7 | As a user, I want logs for troubleshooting. | Timestamped log file written per run with INFO lines for progress and errors. |
| US8 | As a user, I want to choose the destination folder. | Text input accepting path; folder auto-created if absent. |
| US9 | As a user, I want clear progress feedback. | Log lines and (future) per-file progress indicators; success message when complete. |
| US10 | As a user, I need errors handled without crashing. | Exceptions captured; user sees friendly warning; manifest excludes failed entries. |
| US11 | As a user, I want the app to avoid listing folders. | Only non-folder items appear. |
| US12 | As a user, I want the tool to function with large Drives. | Pagination handles >10k items; memory usage bounded (streaming iteration). |

## 4. Functional Requirements
| ID | Requirement | Priority | Trace (Goal/User Story) |
|----|-------------|----------|-------------------------|
| FR1 | Provide OAuth2 desktop flow using user-supplied credentials.json. | Must | G1, US1 |
| FR2 | Store refresh token locally in token.json (same folder). | Must | G1 |
| FR3 | Drive scope limited to drive.readonly. | Must | G1 |
| FR4 | List files excluding folders with fields: id, name, size, mimeType, modifiedTime, md5Checksum. | Must | G2, US3 |
| FR5 | Apply minimum size filter (quotaBytesUsed > threshold). | Must | G2, US2 |
| FR6 | Present inventory in interactive table or selection widget. | Must | G3, US4 |
| FR7 | Download selected files to destination path. | Must | G3, US4 |
| FR8 | Use resumable download with progress logging. | Must | G4, US5 |
| FR9 | Retry failures up to 5 attempts with exponential backoff. | Must | G4, US5 |
| FR10 | Write JSONL manifest lines per file with metadata including checksum if available. | Must | G5, US6 |
| FR11 | Create timestamped log file per run. | Must | G4, US7 |
| FR12 | Allow custom destination and create directories. | Must | G3, US8 |
| FR13 | Provide human-readable file sizes. | Should | US3 |
| FR14 | Display total file count. | Should | US3 |
| FR15 | Modular architecture separating UI, API, utils. | Should | G4 |
| FR16 | Support Shared Drives enumeration. | Should | G2 |
| FR17 | Manifest & logs stored under dedicated folders. | Should | G5 |
| FR18 | No deletion or mutation of Drive data. | Must | NG2 |

## 5. Non-Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR1 | Performance: list 25k files < 120s (API/network permitting). | Should |
| NFR2 | Reliability: >=90% success on first attempt for files <2GB with stable network. | Must |
| NFR3 | Usability: <10 min first-run setup (besides Google project creation). | Should |
| NFR4 | Security: tokens stored locally; no telemetry exfiltration. | Must |
| NFR5 | Maintainability: code modules <300 lines each. | Should |
| NFR6 | Observability: logs + manifest enable post-run audit. | Must |
| NFR7 | Portability: Runs on Windows/macOS/Linux with Python 3.10+. | Should |

## 6. Data Model
- File Inventory Record: {id, name, size, mimeType, modifiedTime, md5}
- Manifest Entry: above + downloadTimestamp
- Log Entry: time, level, message

## 7. Dependencies
- Python 3.10+
- Streamlit
- google-api-python-client, google-auth-* libs
- tenacity, pandas, humanize

## 8. Open Issues
| ID | Issue | Owner | Target |
|----|-------|-------|--------|
| OI1 | Add mime/date filters beyond size. | TBD | Post-MVP |
| OI2 | Free space pre-check before large downloads. | TBD | v1.1 |
| OI3 | Parallel downloads optimization. | TBD | v1.1 |

## 9. Traceability Matrix
Requirements table already maps FR -> Goals/User Stories. Future test cases will reference FR IDs.

## 10. Approval
Stakeholders to sign off in repo PR.
