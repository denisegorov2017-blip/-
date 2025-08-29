@echo off
REM Скрипт для настройки автоматической отправки в Git

echo Установка автоматической отправки изменений в Git...

REM Создаем задачу в планировщике заданий Windows для автоматической отправки
echo Создание задачи в планировщике заданий...

REM Проверяем, существует ли уже задача
schtasks /query /tn "AutoGitPush" >nul 2>&1
if %errorlevel% equ 0 (
    echo Задача AutoGitPush уже существует. Удаляем старую задачу...
    schtasks /delete /tn "AutoGitPush" /f
)

REM Создаем новую задачу, которая будет запускаться каждые 30 минут
schtasks /create /tn "AutoGitPush" /tr "python \"%~dp0auto_git_push.py\"" /sc minute /mo 30 /f

echo.
echo Автоматическая отправка изменений в Git настроена.
echo Задача будет выполняться каждые 30 минут.
echo Для ручного запуска используйте: python scripts\auto_git_push.py
echo.

pause