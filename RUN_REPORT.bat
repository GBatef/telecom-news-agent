@echo off
title Global Telecom News - Generate Report
cd /d "C:\Users\goubaa\Desktop\NET IA agent"
call venv\Scripts\activate
echo Generating today's telecom report...
python main.py --no-content
echo.
echo Done! Check the reports\ folder.
pause
