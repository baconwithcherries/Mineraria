@echo off
REM Try to use the specific Python 3.11 path if it exists, otherwise fall back to 'python'
if exist "C:\Users\james\AppData\Local\Programs\Python\Python311\python.exe" (
    "C:\Users\james\AppData\Local\Programs\Python\Python311\python.exe" -m src.main
) else (
    python -m src.main
)
pause
