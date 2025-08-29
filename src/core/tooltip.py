#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для создания всплывающих подсказок (tooltips) в Tkinter.
"""

import tkinter as tk
from typing import Optional


class ToolTip:
    """
    Класс для создания всплывающих подсказок для виджетов Tkinter.
    """
    
    def __init__(self, widget, text: str = '', delay: int = 500, wraplength: int = 300):
        """
        Инициализирует всплывающую подсказку.
        
        Args:
            widget: Виджет, для которого создается подсказка
            text (str): Текст подсказки
            delay (int): Задержка перед показом подсказки в миллисекундах
            wraplength (int): Максимальная ширина текста подсказки в пикселях
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0
        
        # Привязываем события к виджету
        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<ButtonPress>", self.on_leave, add="+")
    
    def on_enter(self, event=None):
        """Обработчик события наведения курсора на виджет."""
        self.schedule()
    
    def on_leave(self, event=None):
        """Обработчик события ухода курсора с виджета."""
        self.unschedule()
        self.hide_tooltip()
    
    def schedule(self):
        """Планирует показ подсказки с задержкой."""
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tooltip)
    
    def unschedule(self):
        """Отменяет запланированный показ подсказки."""
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def show_tooltip(self, event=None):
        """Показывает всплывающую подсказку."""
        # Получаем позицию курсора
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # Создаем окно подсказки
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Убираем декорации окна
        tw.wm_geometry(f"+{x}+{y}")
        
        # Создаем фрейм для подсказки
        frame = tk.Frame(tw, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        frame.pack()
        
        # Добавляем текст подсказки
        label = tk.Label(
            frame,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            foreground="#000000",
            relief=tk.FLAT,
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=self.wraplength
        )
        label.pack(ipadx=4, ipady=2)
    
    def hide_tooltip(self):
        """Скрывает всплывающую подсказку."""
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()
    
    def set_text(self, text: str):
        """
        Устанавливает текст подсказки.
        
        Args:
            text (str): Новый текст подсказки
        """
        self.text = text


# Функция для удобного добавления подсказок к виджетам
def create_tooltip(widget, text: str, delay: int = 500, wraplength: int = 300) -> ToolTip:
    """
    Создает всплывающую подсказку для виджета.
    
    Args:
        widget: Виджет, для которого создается подсказка
        text (str): Текст подсказки
        delay (int): Задержка перед показом подсказки в миллисекундах
        wraplength (int): Максимальная ширина текста подсказки в пикселях
        
    Returns:
        ToolTip: Созданный объект подсказки
    """
    return ToolTip(widget, text, delay, wraplength)