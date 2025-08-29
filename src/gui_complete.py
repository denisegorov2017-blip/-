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
from core.ai_chat import AIChat  # Добавляем импорт ИИ чата
from core.settings_manager import SettingsManager  # Добавляем импорт менеджера настроек
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

    # Initialize Settings Manager
    settings_manager = SettingsManager()

    # Storage for report path
    report_path_storage = {"path": ""}

    # Initialize AI Chat
    ai_chat = AIChat()

    # File picker
    def pick_files_result(e: FilePickerResultEvent):
        selected_files = e.files
        if selected_files:
            file_path_text.value = selected_files[0].path
        else:
            file_path_text.value = "Файл не выбран"
        page.update()

    file_picker = FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    # UI Components
    title = Text("Система Расчета Коэффициентов Нелинейной Усушки", size=24, weight=ft.FontWeight.BOLD, color=Colors.BLUE_800)
    
    file_path_text = Text("Файл не выбран", size=14, color=Colors.GREY_700)
    pick_file_button = ElevatedButton(
        "Выбрать Excel файл",
        icon=Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type="custom", allowed_extensions=["xlsx", "xls", "xlsm"])
    )
    
    use_adaptive_checkbox = Checkbox(label="Использовать адаптивную модель расчета", value=False)
    
    surplus_rate_input = ft.TextField(label="Процент излишка при поступлении (%)", width=200, value="5.0", disabled=True)
    
    def toggle_surplus_input(e):
        surplus_rate_input.disabled = not use_surplus_checkbox.value
        page.update()
    
    use_surplus_checkbox = Checkbox(label="Учитывать процент излишка при поступлении", value=False, on_change=toggle_surplus_input)
    
    run_button = ElevatedButton(
        "Рассчитать коэффициенты",
        icon=Icons.PLAY_ARROW,
        on_click=lambda _: run_calculation(None),
        bgcolor=Colors.BLUE_600,
        color=Colors.WHITE
    )
    
    status_text = Text("", size=14, color=Colors.BLUE_600)
    progress_bar = ProgressBar(visible=False, color=Colors.BLUE_600)
    
    open_report_button = ElevatedButton(
        "Открыть отчет",
        icon=Icons.VISIBILITY,
        visible=False,
        on_click=lambda _: open_report(None)
    )
    
    open_folder_button = ElevatedButton(
        "Открыть папку с результатами",
        icon=Icons.FOLDER_OPEN,
        visible=False,
        on_click=lambda _: open_results_folder(None)
    )

    def show_snackbar(message, color=Colors.BLUE_500):
        page.snack_bar = ft.SnackBar(Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def animate_button(button):
        original_bgcolor = button.bgcolor
        button.bgcolor = Colors.BLUE_800
        page.update()
        time.sleep(0.1)
        button.bgcolor = original_bgcolor
        page.update()

    def open_report(e):
        report_path = report_path_storage["path"]
        if report_path and os.path.exists(report_path):
            try:
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
                show_snackbar("Отчет открыт в браузере", Colors.GREEN_500)
            except Exception as ex:
                show_snackbar(f"Ошибка открытия отчета: {ex}", Colors.RED_500)
        else:
            show_snackbar("Отчет не найден", Colors.ORANGE_500)

    def open_results_folder(e):
        results_dir = "результаты"
        if os.path.exists(results_dir):
            try:
                os.startfile(os.path.abspath(results_dir))
                show_snackbar("Папка с результатами открыта", Colors.GREEN_500)
            except Exception as ex:
                show_snackbar(f"Ошибка открытия папки: {ex}", Colors.RED_500)
        else:
            show_snackbar("Папка с результатами не найдена", Colors.ORANGE_500)

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
                    system.set_surplus_rate(surplus_rate)
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

    # Help dialog
    def show_help(e):
        help_dialog = ft.AlertDialog(
            title=Text("Помощь", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                Text("Система Расчета Коэффициентов Усушки - Руководство пользователя", size=16, weight=ft.FontWeight.BOLD),
                Text(""),
                Text("ОСНОВНЫЕ ФУНКЦИИ:", size=14, weight=ft.FontWeight.BOLD),
                Text("• Выбор Excel файла через диалог"),
                Text("• Конвертация Excel в JSON с сохранением иерархии"),
                Text("• Парсинг JSON данных"),
                Text("• Расчет коэффициентов усушки"),
                Text("• Генерация HTML отчетов"),
                Text("• Открытие отчетов в браузере"),
                Text("• Открытие папки с результатами"),
                Text("• Автоматическая проверка наличия инвентаризаций"),
                Text("• ИИ-чат для помощи в работе с системой"),
                Text(""),
                Text("ИНФОРМАЦИЯ О ПРОВЕРКЕ ИНВЕНТАРИЗАЦИЙ:", size=14, weight=ft.FontWeight.BOLD),
                Text("Система автоматически проверяет наличие начальной и конечной инвентаризаций в данных."),
                Text("Если инвентаризации отсутствуют, система выводит предупреждение в статусную строку."),
                Text("ВАЖНО: Начальный остаток берется на начало периода по датам инвентаризации."),
                Text("Конечный остаток берется на конец периода по датам инвентаризации."),
                Text("Система работает с теми данными, которые предоставлены, без запроса дополнительного ввода."),
                Text(""),
                Text("ИИ-ЧАТ:", size=14, weight=ft.FontWeight.BOLD),
                Text("Встроенный ИИ-ассистент помогает пользователям понимать работу системы и правильно готовить данные для расчетов."),
                Text("Можно задавать вопросы о работе системы, подготовке данных, интерпретации результатов и т.д."),
                Text(""),
                Text("СИСТЕМНЫЕ НАСТРОЙКИ:", size=14, weight=ft.FontWeight.BOLD),
                Text("• Общие настройки: Тип модели, период расчета, точность, адаптивная модель"),
                Text("• Настройки интерфейса: Тема, язык, размер окна"),
                Text("• Настройки базы данных: Подключение, резервное копирование, верификация"),
                Text("• Настройки вывода: Директория результатов, автоматическое открытие отчетов"),
                Text(""),
                Text("ТЕХНИЧЕСКАЯ ПОДДЕРЖКА:", size=14, weight=ft.FontWeight.BOLD),
                Text("Если у вас возникли проблемы, проверьте:"),
                Text("- Правильность формата Excel файла"),
                Text("- Наличие необходимых колонок в данных"),
                Text("- Достаточные права доступа к файлам"),
            ], scroll=ft.ScrollMode.AUTO, height=400),
            actions=[
                ft.TextButton("Закрыть", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update())
            ],
        )
        page.dialog = help_dialog
        page.dialog.open = True
        page.update()

    # AI Chat components
    chat_history = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
    chat_input = ft.TextField(label="Введите ваш вопрос...", expand=True)
    
    def update_chat_history():
        """Обновляет историю чата в интерфейсе"""
        chat_history.controls.clear()
        for message in ai_chat.get_chat_history():
            role = message["role"]
            content = message["content"]
            timestamp = message["timestamp"][:19].replace("T", " ")
            
            if role == "user":
                chat_history.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Вы ({timestamp})", size=12, color=Colors.BLUE_700),
                            ft.Text(content, size=14)
                        ]),
                        padding=10,
                        border_radius=5,
                        bgcolor=Colors.BLUE_50,
                        width=page.width * 0.7
                    )
                )
            else:
                chat_history.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"ИИ-ассистент ({timestamp})", size=12, color=Colors.GREEN_700),
                            ft.Text(content, size=14)
                        ]),
                        padding=10,
                        border_radius=5,
                        bgcolor=Colors.GREEN_50,
                        width=page.width * 0.7
                    )
                )
        page.update()
    
    def send_message(e):
        """Отправляет сообщение в чат ИИ"""
        user_message = chat_input.value.strip()
        if user_message:
            # Добавляем сообщение пользователя в чат
            ai_chat.add_message("user", user_message)
            update_chat_history()
            
            # Очищаем поле ввода
            chat_input.value = ""
            page.update()
            
            # Получаем ответ от ИИ
            ai_response = ai_chat.get_response(user_message)
            
            # Обновляем интерфейс с ответом ИИ
            update_chat_history()
    
    def clear_chat(e):
        """Очищает историю чата"""
        ai_chat.clear_chat_history()
        update_chat_history()
    
    # Settings dialog for AI chat
    def show_ai_settings(e):
        """Показывает диалог настроек ИИ чата"""
        # Поля настроек
        enable_external_ai = ft.Checkbox(label="Включить внешний ИИ", value=ai_chat.enable_external_ai)
        api_key_field = ft.TextField(label="API ключ", value=ai_chat.external_ai_api_key, password=True)
        base_url_field = ft.TextField(label="Базовый URL", value=ai_chat.external_ai_base_url)
        model_field = ft.Dropdown(
            label="Модель ИИ",
            options=[
                ft.dropdown.Option("gpt-3.5-turbo"),
                ft.dropdown.Option("gpt-4"),
                ft.dropdown.Option("claude-3"),
                ft.dropdown.Option("other")
            ],
            value=ai_chat.external_ai_model
        )
        
        def save_settings(e):
            """Сохраняет настройки ИИ чата"""
            settings = {
                'enable_external_ai': enable_external_ai.value,
                'external_ai_api_key': api_key_field.value,
                'external_ai_model': model_field.value,
                'external_ai_base_url': base_url_field.value
            }
            ai_chat.update_settings(settings)
            page.dialog.open = False
            page.update()
            show_snackbar("Настройки ИИ сохранены", Colors.GREEN_500)
        
        settings_dialog = ft.AlertDialog(
            title=Text("Настройки ИИ-чата", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                enable_external_ai,
                api_key_field,
                base_url_field,
                model_field,
                ft.Text("Примечание: Для использования внешних ИИ сервисов необходимо иметь действующий API ключ.", size=12, color=Colors.GREY_600)
            ], width=400),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.TextButton("Сохранить", on_click=save_settings)
            ],
        )
        page.dialog = settings_dialog
        page.dialog.open = True
        page.update()
    
    # System settings dialog
    def show_system_settings(e):
        """Показывает диалог системных настроек"""
        # Get current settings
        current_model_type = settings_manager.get_setting('model_type', 'exponential')
        current_default_period = settings_manager.get_setting('default_period', 7)
        current_min_accuracy = settings_manager.get_setting('min_accuracy', 50.0)
        current_use_adaptive = settings_manager.get_setting('use_adaptive_model', False)
        current_avg_surplus = settings_manager.get_setting('average_surplus_rate', 0.0) * 100
        current_theme = settings_manager.get_setting('theme', 'light')
        current_language = settings_manager.get_setting('language', 'ru')
        current_window_width = settings_manager.get_setting('window_width', 1200)
        current_window_height = settings_manager.get_setting('window_height', 900)
        current_enable_db = settings_manager.get_setting('enable_database', True)
        current_db_url = settings_manager.get_setting('database_url', 'sqlite:///shrinkage_database.db')
        current_backup_path = settings_manager.get_setting('database_backup_path', 'backups/')
        current_backup_interval = settings_manager.get_setting('database_backup_interval', 24)
        current_enable_verification = settings_manager.get_setting('enable_verification', False)
        current_output_dir = settings_manager.get_setting('output_dir', 'результаты')
        current_auto_open = settings_manager.get_setting('auto_open_reports', True)
        current_report_theme = settings_manager.get_setting('report_theme', 'default')
        
        # Settings fields
        model_type_field = ft.Dropdown(
            label="Тип модели",
            options=[
                ft.dropdown.Option("exponential"),
                ft.dropdown.Option("linear"),
                ft.dropdown.Option("polynomial")
            ],
            value=current_model_type
        )
        
        default_period_field = ft.TextField(label="Период по умолчанию (дней)", value=str(current_default_period), keyboard_type=ft.KeyboardType.NUMBER)
        
        min_accuracy_field = ft.Slider(
            min=0, 
            max=100, 
            divisions=100,
            value=current_min_accuracy,
            label="Мин. точность: {value}%"
        )
        
        use_adaptive_field = ft.Checkbox(label="Использовать адаптивную модель", value=current_use_adaptive)
        
        avg_surplus_field = ft.Slider(
            min=0, 
            max=20, 
            divisions=200,
            value=current_avg_surplus,
            label="Средний излишек: {value}%"
        )
        
        theme_field = ft.Dropdown(
            label="Тема интерфейса",
            options=[
                ft.dropdown.Option("light", "Светлая"),
                ft.dropdown.Option("dark", "Темная"),
                ft.dropdown.Option("system", "Системная")
            ],
            value=current_theme
        )
        
        language_field = ft.Dropdown(
            label="Язык",
            options=[
                ft.dropdown.Option("ru", "Русский"),
                ft.dropdown.Option("en", "English")
            ],
            value=current_language
        )
        
        window_width_field = ft.TextField(label="Ширина окна", value=str(current_window_width), keyboard_type=ft.KeyboardType.NUMBER)
        window_height_field = ft.TextField(label="Высота окна", value=str(current_window_height), keyboard_type=ft.KeyboardType.NUMBER)
        
        enable_db_field = ft.Checkbox(label="Включить базу данных", value=current_enable_db)
        db_url_field = ft.TextField(label="URL базы данных", value=current_db_url)
        backup_path_field = ft.TextField(label="Путь к резервным копиям", value=current_backup_path)
        backup_interval_field = ft.TextField(label="Интервал резервного копирования (часы)", value=str(current_backup_interval), keyboard_type=ft.KeyboardType.NUMBER)
        enable_verification_field = ft.Checkbox(label="Включить верификацию коэффициентов", value=current_enable_verification)
        
        output_dir_field = ft.TextField(label="Директория для результатов", value=current_output_dir)
        auto_open_field = ft.Checkbox(label="Автоматически открывать отчеты", value=current_auto_open)
        
        report_theme_field = ft.Dropdown(
            label="Тема отчетов",
            options=[
                ft.dropdown.Option("default", "По умолчанию"),
                ft.dropdown.Option("dark", "Темная"),
                ft.dropdown.Option("light", "Светлая"),
                ft.dropdown.Option("colorful", "Цветная")
            ],
            value=current_report_theme
        )
        
        # Tabs for different setting categories
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Общие",
                    content=ft.Column([
                        model_type_field,
                        default_period_field,
                        ft.Text("Минимальная точность (%):"),
                        min_accuracy_field,
                        use_adaptive_field,
                        ft.Text("Средний процент излишка (%):"),
                        avg_surplus_field,
                    ], scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text="Интерфейс",
                    content=ft.Column([
                        theme_field,
                        language_field,
                        window_width_field,
                        window_height_field,
                    ], scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text="База данных",
                    content=ft.Column([
                        enable_db_field,
                        db_url_field,
                        backup_path_field,
                        backup_interval_field,
                        enable_verification_field,
                    ], scroll=ft.ScrollMode.AUTO)
                ),
                ft.Tab(
                    text="Вывод",
                    content=ft.Column([
                        output_dir_field,
                        auto_open_field,
                        report_theme_field,
                    ], scroll=ft.ScrollMode.AUTO)
                ),
            ],
            expand=1,
        )
        
        def save_settings(e):
            """Сохраняет системные настройки"""
            try:
                # Validate numeric inputs
                default_period = int(default_period_field.value)
                window_width = int(window_width_field.value)
                window_height = int(window_height_field.value)
                backup_interval = int(backup_interval_field.value)
                
                # Update settings
                new_settings = {
                    'model_type': model_type_field.value,
                    'default_period': default_period,
                    'min_accuracy': min_accuracy_field.value,
                    'use_adaptive_model': use_adaptive_field.value,
                    'average_surplus_rate': avg_surplus_field.value / 100.0,  # Convert from percentage
                    'theme': theme_field.value,
                    'language': language_field.value,
                    'window_width': window_width,
                    'window_height': window_height,
                    'enable_database': enable_db_field.value,
                    'database_url': db_url_field.value,
                    'database_backup_path': backup_path_field.value,
                    'database_backup_interval': backup_interval,
                    'enable_verification': enable_verification_field.value,
                    'output_dir': output_dir_field.value,
                    'auto_open_reports': auto_open_field.value,
                    'report_theme': report_theme_field.value
                }
                
                # Update settings manager
                settings_manager.update_settings(new_settings)
                settings_manager.save_settings()
                
                # Update UI
                use_adaptive_checkbox.value = use_adaptive_field.value
                page.window_width = window_width
                page.window_height = window_height
                
                page.dialog.open = False
                page.update()
                show_snackbar("Системные настройки сохранены", Colors.GREEN_500)
            except ValueError as ex:
                show_snackbar("Ошибка в числовых значениях", Colors.RED_500)
            except Exception as ex:
                show_snackbar(f"Ошибка сохранения настроек: {ex}", Colors.RED_500)
        
        def reset_to_defaults(e):
            """Сбрасывает настройки к значениям по умолчанию"""
            settings_manager.reset_to_defaults()
            page.dialog.open = False
            page.update()
            show_snackbar("Настройки сброшены к значениям по умолчанию", Colors.ORANGE_500)
        
        settings_dialog = ft.AlertDialog(
            title=Text("Системные настройки", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=tabs,
                width=500,
                height=400,
            ),
            actions=[
                ft.TextButton("Сбросить", on_click=reset_to_defaults),
                ft.TextButton("Отмена", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.TextButton("Сохранить", on_click=save_settings)
            ],
        )
        page.dialog = settings_dialog
        page.dialog.open = True
        page.update()
    
    # Initialize chat history
    update_chat_history()

    help_button = ft.IconButton(
        icon=Icons.HELP,
        tooltip="Помощь",
        on_click=show_help
    )
    
    ai_settings_button = ft.IconButton(
        icon=Icons.SETTINGS,
        tooltip="Настройки ИИ",
        on_click=show_ai_settings
    )
    
    system_settings_button = ft.IconButton(
        icon=Icons.SETTINGS_APPLICATIONS,
        tooltip="Системные настройки",
        on_click=show_system_settings
    )

    # Assemble the page
    page.add(
        Row([title, help_button, ai_settings_button, system_settings_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        Divider(height=20, color=Colors.TRANSPARENT),
        Card(
            content=Container(
                content=Column([
                    Text("1. Выберите файл данных", size=16, weight=ft.FontWeight.BOLD),
                    Row([file_path_text, pick_file_button]),
                ], spacing=10),
                padding=20,
            ),
            elevation=3,
        ),
        Divider(height=10, color=Colors.TRANSPARENT),
        Card(
            content=Container(
                content=Column([
                    Text("2. Настройте параметры расчета", size=16, weight=ft.FontWeight.BOLD),
                    use_adaptive_checkbox,
                    use_surplus_checkbox,
                    surplus_rate_input,
                ], spacing=10),
                padding=20,
            ),
            elevation=3,
        ),
        Divider(height=10, color=Colors.TRANSPARENT),
        Card(
            content=Container(
                content=Column([
                    Text("3. Запустите расчет", size=16, weight=ft.FontWeight.BOLD),
                    run_button,
                    progress_bar,
                    status_text,
                    Row([open_report_button, open_folder_button]),
                ], spacing=10),
                padding=20,
            ),
            elevation=3,
        ),
        Divider(height=20, color=Colors.TRANSPARENT),
        Card(
            content=Container(
                content=Column([
                    Text("ИИ-чат", size=16, weight=ft.FontWeight.BOLD),
                    chat_history,
                    Row([
                        chat_input,
                        ft.IconButton(icon=Icons.SEND, on_click=send_message),
                        ft.IconButton(icon=Icons.CLEAR, on_click=clear_chat, tooltip="Очистить чат")
                    ])
                ], spacing=10),
                padding=20,
                height=300
            ),
            elevation=3,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)