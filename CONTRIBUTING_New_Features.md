# Contributing Workflow (Git & GitHub)

This guide explains the standard branch + pull request workflow for adding new features or fixes to FreeUP-Drive.

## Table of Contents
1. Prerequisites
2. Keep `main` Fresh
3. Create a Feature Branch
4. Make & Stage Changes
5. Craft Good Commits
6. Push and Open a Pull Request
7. Updating Your Branch (Rebase vs Merge)
8. Handling Review Feedback
9. Merging & Cleaning Up
10. Tagging a Release (Optional)
11. Useful Recovery / Safety Commands
12. Daily Sync Mini-Routine
13. Commit Quality Checklist
14. Common Pitfalls
15. Optional Enhancements (Hooks, Templates)

---
## 1. Prerequisites
- Git installed.
- Access to the GitHub repo (`git remote -v` should list `origin`).
- Local clone:
```cmd
git clone https://github.com/Sohaniboston/FreeUP-Drive.git
cd FreeUP-Drive
```

## 2. Keep `main` Fresh
Always branch from the latest remote `main`.
```cmd
git checkout main
git pull origin main
```

## 3. Create a Feature Branch
Naming pattern: `feature/<scope>-<short-desc>` or `fix/<issue>`.
```cmd
git checkout -b feature/incremental-mode
```
Other examples: `feature/duplicate-report`, `fix/date-filter-bug`.

## 4. Make & Stage Changes
Edit code, docs, tests. Check status & diff:
```cmd
git status
git diff
```
Stage selectively (recommended):
```cmd
git add src/app.py
```
Add multiple:
```cmd
git add src/app.py src/drive_client.py
```
Stage everything modified/new:
```cmd
git add .
```
Unstage a file:
```cmd
git restore --staged path/to/file
```

## 5. Craft Good Commits
Format: `<type>(scope): imperative summary`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`.
Examples:
```cmd
git commit -m "feat(app): add incremental backup mode using last manifest"
```
Forgot a file?
```cmd
git add missed_file.py
git commit --amend --no-edit
```
Write a multi-line message (opens editor):
```cmd
git commit
```

## 6. Push and Open a Pull Request
First push (sets upstream):
```cmd
git push -u origin feature/incremental-mode
```
Then open GitHub → "Compare & pull request".
PR Template (fill in):
```
Title: feat(app): add incremental backup mode

What & Why:
- Adds UI toggle to set Modified After from last manifest timestamp.

Changes:
- app.py: new incremental toggle + helper
- drive_client.py: no change

Testing:
- Manual scan with/without toggle.

Follow-ups:
- Edge case: no manifest present.

Closes #<issue-if-any>
```

## 7. Updating Your Branch While Waiting for Review
If `main` advanced, rebase (preferred for clean history):
```cmd
git checkout main
git pull origin main
git checkout feature/incremental-mode
git rebase main
```
Resolve conflicts → `git add <files>` →
```cmd
git rebase --continue
```
Push updated history:
```cmd
git push --force-with-lease
```
Why `--force-with-lease`: prevents overwriting others' remote work.

Alternative (merge style – if team prefers):
```cmd
git checkout feature/incremental-mode
git merge main
git push
```

## 8. Handling Review Feedback
Make edits → stage → commit:
```cmd
git add .
git commit -m "refactor(app): address review comments on incremental toggle"
git push
```
Small fixups you want to squash later: prefix with `fix:` or `chore:`.

## 9. Merging & Cleaning Up
After approvals + checks green:
- Use **Squash and merge** (recommended) OR **Rebase and merge**.
- Delete branch on GitHub.
Local cleanup:
```cmd
git checkout main
git pull origin main
git branch -d feature/incremental-mode
git fetch --prune
```

## 10. Tagging a Release (Optional)
```cmd
git tag -a v1.0.1 -m "Incremental mode release"
git push origin v1.0.1
```

## 11. Useful Recovery / Safety Commands
Stash uncommitted work:
```cmd
git stash push -m "wip incremental"
```
List stashes:
```cmd
git stash list
```
Restore & drop latest:
```cmd
git stash pop
```
Keep in stash (apply only):
```cmd
git stash apply
```
Undo last commit but keep changes staged:
```cmd
git reset --soft HEAD~1
```
Undo last commit and unstage changes:
```cmd
git reset HEAD~1
```
Discard local modifications to file:
```cmd
git checkout -- src/app.py
```
Show commit graph (compact):
```cmd
git log --oneline --graph --decorate --all
```

## 12. Daily Sync Mini-Routine
```cmd
git checkout main
git pull origin main
git checkout feature/your-branch
git rebase main
```
If conflicts appear, resolve then continue rebase.

## 13. Commit Quality Checklist
- Single logical change.
- Message clear, imperative, <= 72 chars summary.
- Tests / docs updated if behavior changed.
- No secrets / tokens / large binaries.
- Lint passes (if using linters).

## 14. Common Pitfalls
| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Branch from stale main | Conflicts later | Always pull first |
| Huge "mega" commit | Hard review | Split into logical commits |
| Force push without lease | Overwrites others | Use `--force-with-lease` |
| Commit secrets | Security risk | Rotate creds, purge history |
| Ignoring CI failures | Broken main risk | Fix before merge |

## 15. Optional Enhancements
Create a PR template (`.github/pull_request_template.md`):
```
### What & Why

### Changes

### Testing

### Screenshots (if UI)

### Follow-ups

Closes #
```
Add pre-commit hook (example `.git/hooks/pre-commit`):
```bash
#!/bin/sh
python -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$') || exit 1
```
(Make it executable on Unix; on Windows Git Bash handles it.)

---
Feel free to extend this guide as the team process evolves.
