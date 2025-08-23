@echo off
setlocal enabledelayedexpansion

echo Система расчета коэффициентов усушки
echo =====================================

:: Проверяем наличие виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo Создание виртуального окружения...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo Ошибка создания виртуального окружения!
        pause
        exit /b 1
    )
)

:: Активируем виртуальное окружение
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

:: Проверяем наличие установленных пакетов
python -c "import pandas, numpy, xlrd, openpyxl, PIL" >nul 2>&1
if !errorlevel! neq 0 (
    echo Установка зависимостей...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo Ошибка установки зависимостей!
        pause
        exit /b 1
    )
)

:: Запуск графического интерфейса
echo Запуск графического интерфейса...
python main.py gui

:: Пауза перед закрытием
if !errorlevel! neq 0 (
    echo Произошла ошибка при запуске приложения.
    pause
)

pause