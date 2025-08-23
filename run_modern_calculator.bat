@echo off
setlocal enabledelayedexpansion

echo Современный расчет коэффициентов усушки
echo =======================================

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

:: Запрашиваем дату начала расчета у пользователя
set /p calculation_date=Введите дату начала расчета (ГГГГ-ММ-ДД) или нажмите Enter для использования даты по умолчанию: 

:: Запуск современного расчета коэффициентов усушки
echo Запуск современного расчета коэффициентов усушки...
if defined calculation_date (
    echo Используется дата: %calculation_date%
    python main.py calculate --calculation_start_date %calculation_date%
) else (
    echo Используется дата по умолчанию
    python main.py calculate
)

:: Пауза перед закрытием
if !errorlevel! neq 0 (
    echo Произошла ошибка при запуске расчета.
    pause
)

pause