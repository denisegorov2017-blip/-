#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для взаимодействия с пользователем при обработке данных.

Этот модуль предоставляет функции для запроса подтверждения у пользователя
и получения дополнительной информации при обработке данных инвентаризации.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import os

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from logger_config import log


class UserInteraction:
    """
    Класс для взаимодействия с пользователем во время обработки данных.
    
    Предоставляет методы для запроса подтверждения и получения дополнительной
    информации от пользователя при обработке данных инвентаризации.
    
    ВАЖНО: Начальный остаток берется на начало периода по датам инвентаризации.
    Конечный остаток берется на конец периода по датам инвентаризации.
    """
    
    def __init__(self):
        """Инициализирует модуль взаимодействия с пользователем."""
        log.info("UserInteraction инициализирован")
    
    def confirm_missing_inventory(self, nomenclature: str, filename: str, inventory_type: str = "начальная") -> bool:
        """
        Запрашивает у пользователя подтверждение для продолжения обработки
        при отсутствии инвентаризации.
        
        ВАЖНО: Начальный остаток берется на начало периода по датам инвентаризации.
        Конечный остаток берется на конец периода по датам инвентаризации.
        
        Args:
            nomenclature (str): Название номенклатуры.
            filename (str): Имя файла.
            inventory_type (str): Тип отсутствующей инвентаризации ("начальная" или "конечная").
            
        Returns:
            bool: True, если пользователь подтверждает продолжение, False в противном случае.
        """
        try:
            # Создаем скрытое окно Tkinter для диалога
            root = tk.Tk()
            root.withdraw()  # Скрываем главное окно
            
            # Формируем сообщение для пользователя
            if inventory_type == "начальная":
                message = (f"Для номенклатуры '{nomenclature}' отсутствует начальная инвентаризация (на начало периода по датам).\n\n"
                          f"Файл: {filename}\n\n"
                          f"Хотите продолжить расчет с начальным остатком 0.0 или ввести значение вручную?\n\n"
                          f"ВАЖНО: Начальный остаток берется на начало периода по датам инвентаризации.")
            else:
                message = (f"Для номенклатуры '{nomenclature}' отсутствует конечная инвентаризация (на конец периода по датам).\n\n"
                          f"Файл: {filename}\n\n"
                          f"Хотите продолжить расчет с конечным остатком 0.0 или ввести значение вручную?\n\n"
                          f"ВАЖНО: Конечный остаток берется на конец периода по датам инвентаризации.")
            
            # Показываем диалоговое окно с выбором
            result = messagebox.askyesno("Подтверждение", message, icon='warning')
            
            # Уничтожаем окно
            root.destroy()
            
            return result
        except Exception as e:
            log.error(f"Ошибка при запросе подтверждения у пользователя: {e}")
            # В случае ошибки возвращаем False (не продолжать)
            return False
    
    def get_inventory_balance(self, nomenclature: str, inventory_type: str = "начальную") -> float:
        """
        Запрашивает у пользователя значение остатка по инвентаризации.
        
        ВАЖНО: Начальный остаток берется на начало периода по датам инвентаризации.
        Конечный остаток берется на конец периода по датам инвентаризации.
        
        Args:
            nomenclature (str): Название номенклатуры.
            inventory_type (str): Тип инвентаризации ("начальную" или "конечную").
            
        Returns:
            float: Значение остатка, введенное пользователем на соответствующую дату.
        """
        try:
            # Создаем скрытое окно Tkinter для диалога
            root = tk.Tk()
            root.withdraw()  # Скрываем главное окно
            
            # Показываем диалоговое окно для ввода значения
            balance = simpledialog.askfloat(
                f"{inventory_type.capitalize()} инвентаризацию", 
                f"Введите {inventory_type} остаток для '{nomenclature}' (на соответствующую дату):\n\n"
                f"ВАЖНО: Значение берется на {inventory_type} периода по датам инвентаризации.\n"
                f"Начальный остаток - на начало периода, конечный остаток - на конец периода.",
                minvalue=0.0
            )
            
            # Уничтожаем окно
            root.destroy()
            
            # Если пользователь нажал "Отмена", возвращаем 0.0
            if balance is None:
                return 0.0
                
            return float(balance)
        except Exception as e:
            log.error(f"Ошибка при запросе остатка у пользователя: {e}")
            # В случае ошибки возвращаем 0.0
            return 0.0
    
    def handle_missing_inventory(self, nomenclature: str, filename: str, inventory_type: str = "начальная") -> tuple:
        """
        Обрабатывает случай отсутствия инвентаризации.
        
        Args:
            nomenclature (str): Название номенклатуры.
            filename (str): Имя файла.
            inventory_type (str): Тип отсутствующей инвентаризации ("начальная" или "конечная").
            
        Returns:
            tuple: (continue_processing: bool, balance: float)
        """
        # Запрашиваем подтверждение у пользователя
        if self.confirm_missing_inventory(nomenclature, filename, inventory_type):
            # Если пользователь подтверждает, запрашиваем остаток
            if inventory_type == "начальная":
                balance = self.get_inventory_balance(nomenclature, "начальную")
            else:
                balance = self.get_inventory_balance(nomenclature, "конечную")
            return True, balance
        else:
            # Если пользователь не подтверждает, не продолжаем обработку
            return False, 0.0


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр класса
    interaction = UserInteraction()
    
    # Пример использования методов
    print("🔍 Демонстрация модуля взаимодействия с пользователем")
    print("=" * 50)
    
    # Пример запроса подтверждения
    # result = interaction.confirm_missing_inventory("БЫЧКИ ВЯЛЕНЫЕ", "test_file.xlsx")
    # print(f"Результат подтверждения: {result}")
    
    # Пример запроса начального остатка
    # balance = interaction.get_inventory_balance("БЫЧКИ ВЯЛЕНЫЕ", "начальную")
    # print(f"Введенный начальный остаток: {balance}")
    
    print("Для тестирования раскомментируйте строки выше.")