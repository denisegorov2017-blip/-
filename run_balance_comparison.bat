@echo off
setlocal enabledelayedexpansion

echo Сравнение начальных остатков
echo ==========================

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
python -c "import pandas, numpy, xlrd, openpyxl, PIL, pdfplumber" >nul 2>&1
if !errorlevel! neq 0 (
    echo Установка зависимостей...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo Ошибка установки зависимостей!
        pause
        exit /b 1
    )
)

:: Запуск сравнения начальных остатков
echo Запуск сравнения начальных остатков...
python main.py compare --file1 "исходные_данные/Для_расчета_коэфф/sheet_1_Лист_1.csv" --file2 "исходные_данные/Для_передварительной_усушки/sheet_1_Лист_1_prelim.csv" --output "результаты/сравнение_остатков.csv" --mode detailed

:: Пауза перед закрытием
if !errorlevel! neq 0 (
    echo Произошла ошибка при запуске сравнения начальных остатков.
    pause
)

pause