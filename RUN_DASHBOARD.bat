@echo off
title Global Telecom News Dashboard
cd /d "C:\Users\goubaa\Desktop\NET IA agent"
call venv\Scripts\activate
echo Starting Telecom News Dashboard...
echo Browser will open at http://localhost:8501
streamlit run dashboard.py
pause
