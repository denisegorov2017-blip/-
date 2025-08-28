#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска интерфейсов системы расчета коэффициентов усушки
"""

import os
import sys
import subprocess
import time

def launch_flet_gui():
    """Запуск Flet GUI"""
    print("🚀 Запуск графического интерфейса (Flet)...")
    try:
        # Убедимся, что мы в правильной директории
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        subprocess.run([sys.executable, "-m", "flet", "run", "src/gui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске Flet GUI: {e}")
    except FileNotFoundError:
        print("❌ Flet не найден. Установите его с помощью: pip install flet")

def launch_tkinter_gui():
    """Запуск Tkinter GUI"""
    print("🚀 Запуск графического интерфейса (Tkinter)...")
    try:
        # Убедимся, что мы в правильной директории
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        subprocess.run([sys.executable, "src/tkinter_gui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске Tkinter GUI: {e}")

def launch_streamlit_dashboard():
    """Запуск Streamlit Dashboard"""
    print("🚀 Запуск дашборда (Streamlit)...")
    try:
        # Убедимся, что мы в правильной директории
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/dashboard.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске Streamlit Dashboard: {e}")
    except FileNotFoundError:
        print("❌ Streamlit не найден. Установите его с помощью: pip install streamlit")

def show_menu():
    """Показать меню выбора интерфейса"""
    print("\n" + "="*60)
    print("🔧 Система Расчета Коэффициентов Нелинейной Усушки")
    print("="*60)
    print("Выберите интерфейс для запуска:")
    print("1. 🖥️  Графический интерфейс (Flet)")
    print("2. 🖼️  Графический интерфейс (Tkinter)")
    print("3. 📊 Дашборд (Streamlit)")
    print("4. ❌ Выход")
    print("="*60)

def main():
    """Основная функция запуска"""
    while True:
        show_menu()
        choice = input("Введите номер выбора (1-4): ").strip()
        
        if choice == "1":
            launch_flet_gui()
        elif choice == "2":
            launch_tkinter_gui()
        elif choice == "3":
            launch_streamlit_dashboard()
        elif choice == "4":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Пожалуйста, введите число от 1 до 4.")
        
        # Небольшая пауза перед следующим меню
        time.sleep(1)

if __name__ == "__main__":
    main()