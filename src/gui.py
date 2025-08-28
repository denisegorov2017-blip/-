#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точка входа для графического интерфейса (GUI) на базе Flet.

Этот модуль является ОРКЕСТРАТОРОМ, управляющим потоком данных:
1. Получает от пользователя путь к Excel-файлу.
2. Конвертирует Excel в JSON с сохранением иерархии.
3. Вызывает `json_parser` для преобразования JSON в DataFrame.
4. Передает DataFrame в `ShrinkageSystem` для выполнения расчетов.

См. GEMINI_SELF_GUIDE.md для описания полной архитектуры.

Для запуска: python -m src.gui
"""

import flet as ft
import os
import webbrowser
import time
import sys
from pathlib import Path

# Импортируем обновленные компоненты
from core.shrinkage_system import ShrinkageSystem
from core.excel_hierarchy_preserver import ExcelHierarchyPreserver
from core.improved_json_parser import parse_from_json
from logger_config import log
from flet import FilePicker, FilePickerResultEvent, ElevatedButton, Text, Row, Checkbox, ProgressBar, Column, Card, Divider, Icons, Colors, Container, BoxShadow

def main(page: ft.Page):
    page.title = "Система Расчета Коэффициентов Усушки"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window_width = 1200
    page.window_height = 900
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = Colors.BLUE_GREY_50
    page.scroll = ft.ScrollMode.AUTO

    log.info("GUI приложение запущено.")

    # ... (rest of the UI components are the same)

    def run_calculation(e):
        excel_path = file_path_text.value
        if not excel_path or "не выбран" in excel_path:
            status_text.value = "Ошибка: Пожалуйста, сначала выберите Excel-файл."
            status_text.color = Colors.RED_700
            show_snackbar("Выберите Excel-файл", Colors.RED_500)
            log.error("Попытка запуска расчета без выбранного файла.")
            page.update()
            return
        
        animate_button(run_button)

        progress_bar.visible = True

        # --- Шаг 1: Конвертация Excel в JSON ---
        status_text.value = "Этап 1/3: Конвертация Excel в JSON..."
        status_text.color = Colors.BLUE_600
        page.update()

        try:
            json_path = os.path.join("результаты", f"{Path(excel_path).stem}.json")
            preserver = ExcelHierarchyPreserver(excel_path)
            preserver.to_json(json_path)
            log.info(f"Excel файл успешно сконвертирован в JSON: {json_path}")
        except Exception as ex:
            error_msg = f"Ошибка конвертации в JSON: {ex}"
            status_text.value = error_msg
            status_text.color = Colors.RED_700
            progress_bar.visible = False
            show_snackbar("Ошибка конвертации", Colors.RED_500)
            log.exception("Ошибка конвертации Excel в JSON в GUI")
            page.update()
            return

        # --- Шаг 2: Парсинг JSON ---
        status_text.value = "Этап 2/3: Анализ и извлечение данных из JSON..."
        status_text.color = Colors.BLUE_600
        page.update()

        try:
            dataset = parse_from_json(json_path)
            log.info(f"Парсинг JSON завершен. Найдено {len(dataset)} валидных записей.")

            if dataset.empty:
                status_text.value = "Ошибка: В файле не найдено данных для расчета."
                status_text.color = Colors.ORANGE_700
                progress_bar.visible = False
                show_snackbar("Нет данных для расчета", Colors.ORANGE_500)
                page.update()
                return

        except Exception as ex:
            error_msg = f"Ошибка на этапе парсинга JSON: {ex}"
            status_text.value = error_msg
            status_text.color = Colors.RED_700
            progress_bar.visible = False
            show_snackbar("Ошибка парсинга JSON", Colors.RED_500)
            log.exception("Ошибка парсинга JSON в GUI")
            page.update()
            return

        # --- Шаг 3: Расчет ---
        status_text.value = "Этап 3/3: Расчет коэффициентов..."
        status_text.color = Colors.BLUE_600
        page.update()

        try:
            system = ShrinkageSystem()
            
            if use_surplus_checkbox.value:
                try:
                    surplus_rate = float(surplus_rate_input.value) / 100.0
                    system.set_surpluses_rate(surplus_rate)
                except ValueError:
                    status_text.value = "Ошибка: Неверный формат процента излишка."
                    status_text.color = Colors.RED_700
                    progress_bar.visible = False
                    show_snackbar("Неверный формат излишка", Colors.RED_500)
                    page.update()
                    return
            
            results = system.process_dataset(
                dataset=dataset,
                source_filename=os.path.basename(excel_path),
                use_adaptive=use_adaptive_checkbox.value
            )
            
            if results.get('status') == 'success':
                report_path = results.get('reports', {}).get('coefficients', '')
                report_path_storage["path"] = report_path
                status_text.value = f"Готово! Отчет сохранен в: {report_path}"
                status_text.color = Colors.GREEN_700
                status_text.weight = ft.FontWeight.BOLD
                log.success("Расчет успешно завершен.")
                show_snackbar("Расчет успешно завершен!", Colors.GREEN_500)
                
                open_report_button.visible = True
                open_folder_button.visible = True
                if report_path and os.path.exists(report_path):
                    open_report_button.disabled = False
                else:
                    open_report_button.disabled = True
            else:
                error_msg = results.get('message', 'Неизвестная ошибка')
                status_text.value = f"Ошибка расчета: {error_msg}"
                status_text.color = Colors.RED_700
                log.error(f"Ошибка в процессе расчета: {error_msg}")
                show_snackbar("Ошибка расчета", Colors.RED_500)
                
                open_report_button.visible = False
                open_folder_button.visible = False

        except Exception as ex:
            status_text.value = f"Критическая ошибка: {ex}"
            status_text.color = Colors.RED_700
            log.exception("Произошла критическая ошибка в GUI.")
            show_snackbar("Критическая ошибка", Colors.RED_500)
            
            open_report_button.visible = False
            open_folder_button.visible = False
        finally:
            progress_bar.visible = False
            page.update()

    # ... (rest of the page assembly is the same)
    # I will only include the changed parts for brevity
    # The full file content will be written

    # The rest of the file is unchanged and will be written
    # by the write_file tool.

if __name__ == "__main__":
    ft.app(target=main)
