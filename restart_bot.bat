@echo off
echo Остановка всех процессов Python...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul
echo Запуск бота...
python bot.py
pause