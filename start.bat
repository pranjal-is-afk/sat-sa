@echo off
call venv\Scripts\activate.bat
echo Starting SAT-SA on http://localhost:8000 ...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
