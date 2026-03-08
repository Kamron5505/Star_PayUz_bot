@echo off
echo Остановка всех процессов Python...
taskkill /F /IM python.exe /T 2>nul
echo Все процессы Python остановлены.
timeout /t 3 /nobreak >nul
echo Теперь можно запустить бота: python bot.py
pause