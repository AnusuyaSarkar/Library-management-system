@echo off
cd /d "c:\Users\Anusuya\Documents\student management system"
call .venv\Scripts\activate.bat
start http://127.0.0.1:5000
python run.py
pause
