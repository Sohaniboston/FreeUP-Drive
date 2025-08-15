# Traceability Matrix v1.0

| FR ID | Goal(s) | User Story(ies) | Module(s) | Test Coverage (Planned) |
|-------|---------|-----------------|-----------|-------------------------|
| FR1 | G1 | US1 | drive_client | Auth flow mock test |
| FR2 | G1 | US1 | drive_client | Token persistence test |
| FR3 | G1 | US1 | drive_client | Scope assertion test |
| FR4 | G2 | US3, US12 | drive_client | Listing fields test |
| FR5 | G2 | US2 | drive_client | Size filter test |
| FR6 | G3 | US4 | app | UI selection test (manual initially) |
| FR7 | G3 | US4 | drive_client/app | Download smoke test (mock) |
| FR8 | G4 | US5 | drive_client | Retry logic test |
| FR9 | G4 | US5 | drive_client | Backoff timing (bounded) |
| FR10 | G5 | US6 | drive_client/utils | Manifest line test |
| FR11 | G4 | US7 | utils | Log file creation test |
| FR12 | G3 | US8 | app/utils | Destination creation test |
| FR13 | - | US3 | utils | human_size unit test (done) |
| FR14 | - | US3 | app | Count display test (manual) |
| FR15 | G4 | - | all | Module size lint rule |
| FR16 | G2 | - | drive_client | Shared drive flag test |
| FR17 | G5 | US6 | utils | Manifest dir creation test |
| FR18 | NG2 | - | drive_client | No mutation tests |
