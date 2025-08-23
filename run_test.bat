@echo off

REM Путь к виртуальному окружению
set VENV_PATH=.\venv

REM Путь к скрипту
set SCRIPT_PATH=.\скрипты\improved_coefficient_calculator.py

REM Проверка существования виртуального окружения
if not exist "%VENV_PATH%\Scripts\python.exe" (
    echo Виртуальное окружение не найдено. Пожалуйста, запустите install.bat
    exit /b 1
)

REM Запуск скрипта в тестовом режиме
echo Запуск автоматического теста...
"%VENV_PATH%\Scripts\python.exe" -m unittest discover tests

if %errorlevel% neq 0 (
    echo.
    echo !!!!!!!!!!!!!!!!!!
    echo !!! ТЕСТ ПРОВАЛЕН !!!
    echo !!!!!!!!!!!!!!!!!!
) else (
    echo.
    echo +++++++++++++++++++++++
    echo + ТЕСТ УСПЕШНО ПРОЙДЕН +
    echo +++++++++++++++++++++++
)

pause