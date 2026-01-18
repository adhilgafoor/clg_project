@echo off
echo ========================================================
echo               Django Server Launcher
echo ========================================================
echo.
echo Your IP Address(es):
ipconfig | findstr "IPv4"
echo.
echo ========================================================
echo Starting Django server on 0.0.0.0:8000...
echo You can access the site at http://[YOUR_IP]:8000
echo ========================================================
python manage.py runserver 0.0.0.0:8000
pause
