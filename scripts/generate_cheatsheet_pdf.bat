@echo off
setlocal
if not exist .venv (
  echo [INFO] Creating venv
  py -3.10 -m venv .venv
)
call .venv\Scripts\activate
pip install -q -r requirements.txt
python scripts\generate_cheatsheet_pdf.py
if exist docs\GOOGLE_DRIVE_API_CHEATSHEET.pdf (
  echo [SUCCESS] PDF generated at docs\GOOGLE_DRIVE_API_CHEATSHEET.pdf
) else (
  echo [ERROR] PDF generation failed
)
endlocal
