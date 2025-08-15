# High Level Design (HLD)
Project: Google Drive Auto Backup Utility  
Version: 1.0  
Date: 2025-08-14

## 1. Architectural Overview
Layered modular architecture separating Presentation (Streamlit UI), Domain/Service (Drive adapter + download logic), Utilities (logging, size formatting), and Persistence Artifacts (logs, manifests, downloaded files). Data flows: User triggers auth -> OAuth tokens -> Drive Service -> File Listing Stream -> UI selection -> Download Engine -> Local Files + Manifest + Logs.

## 2. Component Diagram (Textual)
- UI (Streamlit `app.py`)
  - Renders controls (auth button, filters, destination input, selection widgets)
  - Invokes service functions for list & download
- Drive Client (`drive_client.py`)
  - Auth management & token storage
  - File listing generator (pagination abstraction)
  - Resumable download function with retry
- Utilities (`utils.py`)
  - Directory setup, logging init, formatting helpers
  - Manifest writing helper
- Artifacts
  - `logs/` timestamped log files
  - `manifests/` JSONL manifests
  - `downloads/` user-chosen destination (default)
  - `secrets/` credentials.json + token.json

## 3. Data Flow (Steps)
1. User launches Streamlit app.
2. User clicks Authenticate; OAuth flow obtains credentials & stores token.
3. User sets filters & initiates scan.
4. UI iterates generator, accumulating file records in session_state.
5. User selects files & triggers download.
6. For each file: Drive media request -> chunked download -> local file system.
7. After each file: log progress, append manifest entry.
8. Completion message returned to user.

## 4. Key Design Decisions
| Decision | Rationale |
|----------|-----------|
| Streamlit for UI | Rapid prototyping, minimal boilerplate, local-first security |
| JSONL manifest | Append-only, easy diffing & streaming write |
| Read-only scope | Minimizes risk, fosters trust |
| tenacity retries | Simplifies robust retry logic |
| Chunked download | Resilience against network hiccups |

## 5. External Integrations
- Google Drive API v3 over HTTPS using `google-api-python-client`.

## 6. Security Considerations
- Tokens stored only locally (no cloud sync assumption).
- Scope restricted to read-only.
- User instructed to protect `secrets/` directory; gitignore recommended (future commit).

## 7. Performance Considerations
- Generator-based listing avoids retaining entire API responses.
- Pagination size adjustable (default 1000) balancing memory & request count.
- Future: parallel downloads with thread pool for high-latency networks.

## 8. Error Handling Strategy
- Download retries with exponential backoff (up to 5 attempts).
- Auth errors surface via UI alerts.
- Logging at INFO; upgrade to WARNING/ERROR for notable failures.

## 9. Observability
- Structured (plain text) logs + progress messages.
- Manifest lines enable correlation between initial metadata & downloaded file.

## 10. Scalability & Extensibility
- Additional filters (mime/date/owner) can be appended to query builder.
- Incremental diff mode can persist last manifest snapshot.
- Encryption/compression can wrap post-download step.

## 11. Deployment & Distribution
- Local run via `streamlit run`.
- Optional packaging as PyInstaller executable (v1.1 consideration).

## 12. Risks & Mitigations (Summarized)
See PRD; addressed via retries, scoping, manifests.

## 13. Open Questions
- Should we hash locally downloaded content for integrity beyond md5Checksum? (Future if checksum missing)
- Provide CLI mode? Potential v1.2.

## 14. Glossary
- Manifest: Line-delimited JSON metadata file for downloaded items.
- Chunked/Resumable Download: Partial retrieval with restart capability.
