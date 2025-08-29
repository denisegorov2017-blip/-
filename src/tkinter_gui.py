import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import webbrowser
import threading
from pathlib import Path
import sys
from datetime import datetime

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import core modules
from src.core.shrinkage_system import ShrinkageSystem
from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
from src.core.improved_json_parser import parse_from_json
from src.core.specialized_fish_data_processor import FishBatchDataProcessor
from src.core.test_data_manager import TestDataManager
from src.core.ai_chat import AIChat  # Добавляем импорт ИИ чата
from src.core.settings_manager import SettingsManager  # Добавляем импорт менеджера настроек
from src.core.tooltip import create_tooltip  # Добавляем импорт tooltip
from src.logger_config import log


class ShrinkageCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Система Расчета Коэффициентов Усушки")
        
        # Initialize Settings Manager
        self.settings_manager = SettingsManager()
        
        # Load window settings
        window_width = self.settings_manager.get_setting('window_width', 1100)
        window_height = self.settings_manager.get_setting('window_height', 750)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(900, 650)
        
        # Initialize AI Chat
        self.ai_chat = AIChat()
        
        # Configure modern styles
        self.setup_styles()
        
        # Variables
        self.file_path = tk.StringVar()
        self.use_adaptive = tk.BooleanVar(value=self.settings_manager.get_setting('use_adaptive_model', False))
        self.use_surplus = tk.BooleanVar(value=False)
        self.surplus_rate = tk.StringVar(value="5.0")
        self.status_text = tk.StringVar(value="Готов к работе")
        self.report_path = None
        self.error_report_path = None
        self.use_fish_batch_mode = tk.BooleanVar(value=False)
        
        # Create UI
        self.create_widgets()
        
        # Initialize status
        self.update_status("Система готова к работе. Выберите Excel файл для начала расчета.")
        
    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#f8fafc')
        style.configure('TLabelframe', background='#f8fafc')
        style.configure('TLabelframe.Label', background='#f8fafc', foreground='#0f172a', font=('Segoe UI', 10, 'bold'))
        
        # Configure buttons
        style.configure('Accent.TButton', 
                       foreground='white', 
                       background='#6366f1',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        style.map('Accent.TButton',
                 background=[('active', '#4f46e5'), ('pressed', '#4338ca')])
        
        style.configure('Secondary.TButton',
                       foreground='#0f172a',
                       background='#e2e8f0',
                       font=('Segoe UI', 10),
                       padding=(15, 8))
        style.map('Secondary.TButton',
                 background=[('active', '#cbd5e1'), ('pressed', '#94a3b8')])
        
        # Configure labels
        style.configure('Title.TLabel', 
                       background='#f8fafc',
                       foreground='#0f172a',
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#f8fafc',
                       foreground='#64748b',
                       font=('Segoe UI', 11))
        
        # Configure entry
        style.configure('TEntry',
                       fieldbackground='white',
                       foreground='#0f172a',
                       font=('Segoe UI', 10))
        
        # Configure checkbutton
        style.configure('TCheckbutton',
                       background='#f8fafc',
                       foreground='#0f172a',
                       font=('Segoe UI', 10))
        
        # Configure radiobutton
        style.configure('TRadiobutton',
                       background='#f8fafc',
                       foreground='#0f172a',
                       font=('Segoe UI', 10))
        
    def create_widgets(self):
        """Create all GUI widgets with modern design"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Системные настройки", command=self.show_system_settings)
        settings_menu.add_command(label="Настройки ИИ-чата", command=self.show_ai_settings)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        title_label = ttk.Label(header_frame, text="Система Расчета Коэффициентов Усушки", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Анализ и расчет коэффициентов нелинейной усушки продукции", style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Content area with notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab
        main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(main_tab, text="  Основное  ")
        
        # File selection section
        file_frame = ttk.LabelFrame(main_tab, text="Выбор файла данных", padding="20")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X)
        
        self.file_entry = ttk.Entry(file_input_frame, textvariable=self.file_path, font=('Segoe UI', 10))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_input_frame, text="Обзор...", command=self.browse_file, style='Secondary.TButton')
        browse_btn.pack(side=tk.RIGHT)
        
        # Processing mode section
        mode_frame = ttk.LabelFrame(main_tab, text="Режим обработки", padding="20")
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Standard processing mode
        standard_radio = ttk.Radiobutton(mode_frame, 
                                        text="Стандартная обработка (общий формат Excel)", 
                                        variable=self.use_fish_batch_mode, 
                                        value=False)
        standard_radio.pack(anchor=tk.W, pady=(0, 10))
        
        # Fish batch processing mode
        fish_radio = ttk.Radiobutton(mode_frame, 
                                    text="Специализированная обработка партий рыбы (специфический формат)", 
                                    variable=self.use_fish_batch_mode, 
                                    value=True)
        fish_radio.pack(anchor=tk.W)
        
        # Options section
        options_frame = ttk.LabelFrame(main_tab, text="Параметры расчета", padding="20")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Adaptive model checkbox
        adaptive_check = ttk.Checkbutton(options_frame, 
                                        text="Использовать адаптивную модель расчета", 
                                        variable=self.use_adaptive)
        adaptive_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Surplus options
        surplus_check = ttk.Checkbutton(options_frame, 
                                       text="Учитывать процент излишка при поступлении:", 
                                       variable=self.use_surplus,
                                       command=self.toggle_surplus_entry)
        surplus_check.pack(anchor=tk.W)
        
        surplus_input_frame = ttk.Frame(options_frame)
        surplus_input_frame.pack(fill=tk.X, padx=(25, 0), pady=(10, 0))
        
        self.surplus_entry = ttk.Entry(surplus_input_frame, 
                                      textvariable=self.surplus_rate, 
                                      width=10,
                                      state="disabled")
        self.surplus_entry.pack(side=tk.LEFT)
        
        ttk.Label(surplus_input_frame, text="%").pack(side=tk.LEFT, padx=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_tab)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.calculate_btn = ttk.Button(button_frame, 
                                       text="Рассчитать коэффициенты", 
                                       command=self.start_calculation,
                                       style='Accent.TButton')
        self.calculate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.report_btn = ttk.Button(button_frame, 
                                    text="Открыть отчет", 
                                    command=self.open_report,
                                    state="disabled",
                                    style='Secondary.TButton')
        self.report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.error_report_btn = ttk.Button(button_frame, 
                                          text="Открыть отчет об ошибках", 
                                          command=self.open_error_report,
                                          state="disabled",
                                          style='Secondary.TButton')
        self.error_report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_tab, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(main_tab, text="Статус выполнения", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_display = scrolledtext.ScrolledText(status_frame, 
                                                       height=12,
                                                       state="disabled",
                                                       wrap=tk.WORD,
                                                       font=('Consolas', 9),
                                                       bg='#f1f5f9',
                                                       fg='#0f172a')
        self.status_display.pack(fill=tk.BOTH, expand=True)
        
        # Utilities tab
        utilities_tab = ttk.Frame(notebook, padding="10")
        notebook.add(utilities_tab, text="  Утилиты  ")
        
        utilities_frame = ttk.LabelFrame(utilities_tab, text="Управление данными", padding="20")
        utilities_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(utilities_frame, text="Инструменты для управления тестовыми данными и очистки файлов:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        self.test_data_btn = ttk.Button(utilities_frame, 
                                       text="Организовать тестовые данные", 
                                       command=self.organize_test_data,
                                       style='Accent.TButton')
        self.test_data_btn.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(utilities_frame, 
                  text="Открыть папку с результатами", 
                  command=self.open_results_folder,
                  style='Secondary.TButton').pack(anchor=tk.W)
        
        ttk.Label(utilities_frame, text="Эта функция автоматически сортирует файлы в подпапки и удаляет старые тестовые данные.", 
                 font=('Segoe UI', 9), 
                 foreground='#64748b').pack(anchor=tk.W, pady=(10, 0))
        
        # AI Chat tab
        chat_tab = ttk.Frame(notebook, padding="10")
        notebook.add(chat_tab, text="  ИИ-чат  ")
        
        chat_frame = ttk.LabelFrame(chat_tab, text="ИИ-ассистент", padding="15")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chat history display
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                     height=20,
                                                     state="disabled",
                                                     wrap=tk.WORD,
                                                     font=('Segoe UI', 10),
                                                     bg='white',
                                                     fg='#0f172a')
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat input area
        chat_input_frame = ttk.Frame(chat_frame)
        chat_input_frame.pack(fill=tk.X)
        
        self.chat_input = ttk.Entry(chat_input_frame, font=('Segoe UI', 10))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', self.send_chat_message)
        
        send_btn = ttk.Button(chat_input_frame, text="Отправить", command=self.send_chat_message, style='Accent.TButton')
        send_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(chat_input_frame, text="Очистить", command=self.clear_chat, style='Secondary.TButton')
        clear_btn.pack(side=tk.LEFT)
        
        # AI Settings button
        settings_btn = ttk.Button(chat_frame, text="Настройки ИИ", command=self.show_ai_settings, style='Secondary.TButton')
        settings_btn.pack(anchor=tk.W, pady=(10, 0))
        
        # Initialize chat display
        self.update_chat_display()
        
        # Help tab
        help_tab = ttk.Frame(notebook, padding="20")
        notebook.add(help_tab, text="  Помощь  ")
        
        help_text = scrolledtext.ScrolledText(help_tab, 
                                             wrap=tk.WORD,
                                             font=('Segoe UI', 10),
                                             bg='white',
                                             fg='#0f172a')
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """Система Расчета Коэффициентов Усушки - Руководство пользователя

ОСНОВНЫЕ ФУНКЦИИ:
• Стандартная обработка: Для общих форматов Excel файлов
• Специализированная обработка: Для партий рыбы с датами прихода и инвентаризации
• Адаптивная модель: Самообучающаяся модель для повышения точности
• Учет излишка: Возможность учета процента излишка при поступлении
• Проверка инвентаризаций: Автоматическая проверка наличия начальной и конечной инвентаризаций
• ИИ-чат: Встроенный ИИ-ассистент для помощи в работе с системой

КАК ИСПОЛЬЗОВАТЬ:
1. Выберите Excel файл с данными
2. Выберите режим обработки (стандартный или специализированный)
3. Настройте параметры расчета
4. Нажмите "Рассчитать коэффициенты"
5. Откройте отчеты для просмотра результатов

СИСТЕМНЫЕ НАСТРОЙКИ:
• Общие настройки: Тип модели, период расчета, точность, адаптивная модель
• Настройки интерфейса: Тема, язык, размер окна
• Настройки базы данных: Подключение, резервное копирование, верификация
• Настройки вывода: Директория результатов, автоматическое открытие отчетов

ИИ-ЧАТ:
Встроенный ИИ-ассистент помогает пользователям понимать работу системы и правильно готовить данные для расчетов.
Можно задавать вопросы о работе системы, подготовке данных, интерпретации результатов и т.д.
В настройках можно подключить внешние ИИ-сервисы (OpenAI, Claude и др.) при наличии API ключа.

ОТЧЕТЫ:
• Основной отчет: Коэффициенты усушки с интерактивной таблицей
• Отчет об ошибках: Детальная информация об ошибках расчета
• Темная/светлая тема: Автоматическое переключение по предпочтениям системы

ТЕХНИЧЕСКАЯ ПОДДЕРЖКА:
Если у вас возникли проблемы, проверьте:
- Правильность формата Excel файла
- Наличие необходимых колонок в данных
- Достаточные права доступа к файлам
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state="disabled")
    
    def toggle_surplus_entry(self):
        """Enable/disable surplus entry based on checkbox"""
        if self.use_surplus.get():
            self.surplus_entry.config(state="normal")
        else:
            self.surplus_entry.config(state="disabled")
    
    def browse_file(self):
        """Open file dialog to select Excel file"""
        file_path = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[
                ("Excel файлы", "*.xlsx *.xls *.xlsm"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            self.file_path.set(file_path)
            self.update_status(f"Выбран файл: {file_path}")
    
    def update_status(self, message):
        """Update status display with new message"""
        self.status_display.config(state="normal")
        self.status_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.status_display.see(tk.END)
        self.status_display.config(state="disabled")
        self.root.update_idletasks()
    
    def start_calculation(self):
        """Start calculation in a separate thread"""
        if not self.file_path.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите Excel файл для расчета")
            return
        
        # Start calculation in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.run_calculation)
        thread.daemon = True
        thread.start()
    
    def run_calculation(self):
        """Run the calculation process"""
        try:
            # Disable UI elements during calculation
            self.calculate_btn.config(state="disabled")
            self.progress.start()
            self.report_btn.config(state="disabled")
            self.error_report_btn.config(state="disabled")
            
            excel_path = self.file_path.get()
            self.update_status("=" * 50)
            self.update_status("Начало расчета...")
            
            # Check if we're using fish batch mode
            if self.use_fish_batch_mode.get():
                self.update_status("Используется специализированный режим обработки партий рыбы...")
                try:
                    processor = FishBatchDataProcessor()
                    results = processor.calculate_shrinkage_for_batches(
                        excel_path, 
                        use_adaptive=self.use_adaptive.get()
                    )
                    
                    if results.get('status') == 'success':
                        self.report_path = results.get('reports', {}).get('coefficients', '')
                        self.error_report_path = results.get('reports', {}).get('errors', '')
                        summary = results.get('summary', {})
                        self.update_status(f"Готово! Обработано {summary.get('total_positions', 0)} позиций")
                        self.update_status(f"Средняя точность: {summary.get('avg_accuracy', 0):.2f}%")
                        self.update_status(f"Ошибок: {summary.get('error_count', 0)}")
                        self.update_status(f"Отчет сохранен в: {self.report_path}")
                        log.info("Расчет успешно завершен.")
                        
                        # Enable report buttons if reports exist
                        if self.report_path and os.path.exists(self.report_path):
                            self.report_btn.config(state="normal")
                        if self.error_report_path and os.path.exists(self.error_report_path):
                            self.error_report_btn.config(state="normal")
                    else:
                        error_msg = results.get('message', 'Неизвестная ошибка')
                        self.update_status(f"Ошибка расчета: {error_msg}")
                        log.error(f"Ошибка в процессе расчета: {error_msg}")
                except Exception as ex:
                    self.update_status(f"Критическая ошибка: {ex}")
                    log.exception("Произошла критическая ошибка в специализированном процессоре.")
            else:
                # Standard processing mode
                # Step 1: Convert Excel to JSON
                self.update_status("Этап 1/3: Конвертация Excel в JSON...")
                json_path = os.path.join("результаты", f"{Path(excel_path).stem}.json")
                
                try:
                    preserver = ExcelHierarchyPreserver(excel_path)
                    preserver.to_json(json_path)
                    self.update_status(f"Excel файл успешно сконвертирован в JSON: {json_path}")
                except Exception as ex:
                    error_msg = f"Ошибка конвертации в JSON: {ex}"
                    self.update_status(error_msg)
                    log.exception("Ошибка конвертации Excel в JSON в GUI")
                    return
                
                # Step 2: Parse JSON
                self.update_status("Этап 2/3: Анализ и извлечение данных из JSON...")
                try:
                    dataset = parse_from_json(json_path)
                    self.update_status(f"Парсинг JSON завершен. Найдено {len(dataset)} валидных записей.")
                    
                    if dataset.empty:
                        self.update_status("Ошибка: В файле не найдено данных для расчета.")
                        return
                except Exception as ex:
                    error_msg = f"Ошибка на этапе парсинга JSON: {ex}"
                    self.update_status(error_msg)
                    log.exception("Ошибка парсинга JSON в GUI")
                    return
                
                # Step 3: Calculate coefficients
                self.update_status("Этап 3/3: Расчет коэффициентов...")
                try:
                    system = ShrinkageSystem()
                    
                    # Set surplus rate if needed
                    if self.use_surplus.get():
                        try:
                            surplus_rate = float(self.surplus_rate.get()) / 100.0
                            system.set_surplus_rate(surplus_rate)
                        except ValueError:
                            self.update_status("Ошибка: Неверный формат процента излишка.")
                            return
                    
                    # Process dataset
                    results = system.process_dataset(
                        dataset=dataset,
                        source_filename=os.path.basename(excel_path),
                        use_adaptive=self.use_adaptive.get()
                    )
                    
                    if results.get('status') == 'success':
                        self.report_path = results.get('reports', {}).get('coefficients', '')
                        self.error_report_path = results.get('reports', {}).get('errors', '')
                        summary = results.get('summary', {})
                        self.update_status(f"Готово! Обработано {summary.get('total_positions', 0)} позиций")
                        self.update_status(f"Средняя точность: {summary.get('avg_accuracy', 0):.2f}%")
                        self.update_status(f"Ошибок: {summary.get('error_count', 0)}")
                        self.update_status(f"Отчет сохранен в: {self.report_path}")
                        log.info("Расчет успешно завершен.")
                        
                        # Enable report buttons if reports exist
                        if self.report_path and os.path.exists(self.report_path):
                            self.report_btn.config(state="normal")
                        if self.error_report_path and os.path.exists(self.error_report_path):
                            self.error_report_btn.config(state="normal")
                    else:
                        error_msg = results.get('message', 'Неизвестная ошибка')
                        self.update_status(f"Ошибка расчета: {error_msg}")
                        log.error(f"Ошибка в процессе расчета: {error_msg}")
                except Exception as ex:
                    self.update_status(f"Критическая ошибка: {ex}")
                    log.exception("Произошла критическая ошибка в GUI.")
        except Exception as ex:
            self.update_status(f"Неожиданная ошибка: {ex}")
            log.exception("Неожиданная ошибка в GUI.")
        finally:
            # Re-enable UI elements
            self.calculate_btn.config(state="normal")
            self.progress.stop()
            self.update_status("=" * 50)
    
    def open_report(self):
        """Open the generated report in browser"""
        if self.report_path and os.path.exists(self.report_path):
            try:
                webbrowser.open(f"file://{os.path.abspath(self.report_path)}")
                self.update_status("Отчет открыт в браузере")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть отчет: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Отчет не найден")
    
    def open_error_report(self):
        """Open the error report in browser"""
        if self.error_report_path and os.path.exists(self.error_report_path):
            try:
                webbrowser.open(f"file://{os.path.abspath(self.error_report_path)}")
                self.update_status("Отчет об ошибках открыт в браузере")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть отчет об ошибках: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Отчет об ошибках не найден")
    
    def open_results_folder(self):
        """Open the results folder in file explorer"""
        results_dir = "результаты"
        if os.path.exists(results_dir):
            try:
                os.startfile(os.path.abspath(results_dir))  # For Windows
                self.update_status("Папка с результатами открыта")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Папка с результатами не найдена")
    
    def organize_test_data(self):
        """Organize test data in separate folders and clean up old files"""
        try:
            self.update_status("Организация тестовых данных...")
            manager = TestDataManager()
            manager.organize_existing_files()
            manager.cleanup_old_test_data()
            stats = manager.get_test_data_stats()
            self.update_status(f"Организация завершена. Тестовых файлов: {stats['test_files_count']}, Реальных файлов: {stats['real_files_count']}")
        except Exception as e:
            self.update_status(f"Ошибка при организации тестовых данных: {e}")
            log.exception("Ошибка при организации тестовых данных")
    
    # AI Chat methods
    def update_chat_display(self):
        """Update the chat display with current chat history"""
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        
        for message in self.ai_chat.get_chat_history():
            role = message["role"]
            content = message["content"]
            timestamp = message["timestamp"][:19].replace("T", " ")
            
            if role == "user":
                self.chat_display.insert(tk.END, f"Вы ({timestamp}):\n", "user_timestamp")
                self.chat_display.insert(tk.END, f"{content}\n\n", "user_message")
            else:
                self.chat_display.insert(tk.END, f"ИИ-ассистент ({timestamp}):\n", "ai_timestamp")
                self.chat_display.insert(tk.END, f"{content}\n\n", "ai_message")
        
        # Configure tags for styling
        self.chat_display.tag_config("user_timestamp", foreground="#6366f1", font=('Segoe UI', 9, 'bold'))
        self.chat_display.tag_config("user_message", foreground="#0f172a", font=('Segoe UI', 10))
        self.chat_display.tag_config("ai_timestamp", foreground="#10b981", font=('Segoe UI', 9, 'bold'))
        self.chat_display.tag_config("ai_message", foreground="#0f172a", font=('Segoe UI', 10))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")
    
    def send_chat_message(self, event=None):
        """Send a message to the AI chat"""
        user_message = self.chat_input.get().strip()
        if user_message:
            # Add user message to chat
            self.ai_chat.add_message("user", user_message)
            
            # Clear input field
            self.chat_input.delete(0, tk.END)
            
            # Update display
            self.update_chat_display()
            
            # Get AI response
            ai_response = self.ai_chat.get_response(user_message)
            
            # Update display with AI response
            self.update_chat_display()
    
    def clear_chat(self):
        """Clear the chat history"""
        self.ai_chat.clear_chat_history()
        self.update_chat_display()
    
    def show_ai_settings(self):
        """Show AI settings dialog"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки ИИ-чата")
        settings_window.geometry("500x600")
        settings_window.resizable(False, False)
        settings_window.configure(bg='#f8fafc')
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === Built-in AI Tab ===
        builtin_frame = ttk.Frame(notebook, padding="20")
        notebook.add(builtin_frame, text="Встроенный ИИ")
        
        ttk.Label(builtin_frame, text="Встроенный ИИ", font=('Segoe UI', 14, 'bold'), 
                 background='#f8fafc').pack(pady=(0, 15))
        
        ttk.Label(builtin_frame, text="Встроенный ИИ работает без подключения к интернету и не требует дополнительных настроек.", 
                 font=('Segoe UI', 10), wraplength=400, background='#f8fafc').pack(anchor=tk.W)
        
        # === External AI Tab ===
        external_frame = ttk.Frame(notebook, padding="20")
        notebook.add(external_frame, text="Внешний ИИ")
        
        # Variables for external AI settings
        enable_external_ai = tk.BooleanVar(value=self.ai_chat.enable_external_ai)
        external_api_key = tk.StringVar(value=self.ai_chat.external_ai_api_key)
        external_model = tk.StringVar(value=self.ai_chat.external_ai_model)
        external_base_url = tk.StringVar(value=self.ai_chat.external_ai_base_url)
        
        ttk.Label(external_frame, text="Внешний ИИ", font=('Segoe UI', 14, 'bold'), 
                 background='#f8fafc').pack(pady=(0, 15))
        
        # Enable external AI checkbox
        ttk.Checkbutton(external_frame, text="Включить внешний ИИ", variable=enable_external_ai).pack(anchor=tk.W)
        
        # API Key entry
        api_frame = ttk.LabelFrame(external_frame, text="API ключ", padding="10")
        api_frame.pack(fill=tk.X, pady=10)
        
        api_entry = ttk.Entry(api_frame, textvariable=external_api_key, show="*", width=40)
        api_entry.pack(fill=tk.X)
        
        # Base URL entry
        url_frame = ttk.LabelFrame(external_frame, text="Базовый URL", padding="10")
        url_frame.pack(fill=tk.X, pady=10)
        
        url_entry = ttk.Entry(url_frame, textvariable=external_base_url, width=40)
        url_entry.pack(fill=tk.X)
        
        # Model selection
        model_frame = ttk.LabelFrame(external_frame, text="Модель ИИ", padding="10")
        model_frame.pack(fill=tk.X, pady=10)
        
        external_model_combo = ttk.Combobox(model_frame, textvariable=external_model, 
                                  values=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-haiku", "claude-3-sonnet", "other"],
                                  state="readonly", width=37)
        external_model_combo.pack(fill=tk.X)
        
        # Добавляем tooltip для внешней модели
        external_model_tooltip = create_tooltip(external_model_combo, 
            "Выберите модель внешнего ИИ:\n\n"
            "• gpt-3.5-turbo - Быстрая и экономичная модель OpenAI\n"
            "• gpt-4 - Более мощная модель OpenAI с лучшим пониманием\n"
            "• gpt-4-turbo - Самая современная модель OpenAI\n"
            "• claude-3-haiku - Быстрая модель Anthropic\n"
            "• claude-3-sonnet - Сбалансированная модель Anthropic\n"
            "• other - Другая модель (укажите в настройках API)")
        
        ttk.Label(external_frame, text="Примечание: Для использования внешних ИИ сервисов необходимо иметь действующий API ключ.",
                 font=('Segoe UI', 9), foreground='#64748b', wraplength=400).pack(anchor=tk.W, pady=(10, 0))
        
        # === Local AI Tab ===
        local_frame = ttk.Frame(notebook, padding="20")
        notebook.add(local_frame, text="Локальный ИИ")
        
        # Variables for local AI settings
        enable_local_ai = tk.BooleanVar(value=self.ai_chat.enable_local_ai)
        local_model = tk.StringVar(value=self.ai_chat.local_ai_model)
        local_base_url = tk.StringVar(value=self.ai_chat.local_ai_base_url)
        
        ttk.Label(local_frame, text="Локальный ИИ (LM Studio)", font=('Segoe UI', 14, 'bold'), 
                 background='#f8fafc').pack(pady=(0, 15))
        
        # Enable local AI checkbox
        ttk.Checkbutton(local_frame, text="Включить локальный ИИ", variable=enable_local_ai).pack(anchor=tk.W)
        
        # Base URL entry
        local_url_frame = ttk.LabelFrame(local_frame, text="URL сервера LM Studio", padding="10")
        local_url_frame.pack(fill=tk.X, pady=10)
        
        local_url_entry = ttk.Entry(local_url_frame, textvariable=local_base_url, width=40)
        local_url_entry.pack(fill=tk.X)
        ttk.Label(local_url_frame, text="По умолчанию: http://localhost:1234/v1", 
                 font=('Segoe UI', 9), foreground='#64748b').pack(anchor=tk.W, pady=(5, 0))
        
        # Model selection
        local_model_frame = ttk.LabelFrame(local_frame, text="Модель локального ИИ", padding="10")
        local_model_frame.pack(fill=tk.X, pady=10)
        
        local_model_combo = ttk.Combobox(local_model_frame, textvariable=local_model, 
                                        values=["gpt-3.5-turbo", "gpt-4", "llama3", "qwen", "gemma", "mistral", "other"],
                                        state="readonly", width=37)
        local_model_combo.pack(fill=tk.X)
        
        # Добавляем tooltip для локальной модели
        local_model_tooltip = create_tooltip(local_model_combo,
            "Выберите модель локального ИИ:\n\n"
            "• gpt-3.5-turbo - Совместимая модель OpenAI\n"
            "• gpt-4 - Совместимая модель OpenAI\n"
            "• llama3 - Модель Meta (рекомендуется для русского языка)\n"
            "• qwen - Модель Alibaba с отличной поддержкой русского языка\n"
            "• gemma - Модель Google\n"
            "• mistral - Модель Mistral AI\n"
            "• other - Другая модель (укажите в настройках LM Studio)\n\n"
            "Рекомендации:\n"
            "• Для 8 ГБ RAM: qwen-4b или gemma-4b\n"
            "• Для 16 ГБ RAM: llama3-8b или qwen-8b\n"
            "• Для 32+ ГБ RAM: llama3-70b или mistral-large")
        
        ttk.Label(local_frame, text="Примечание: Для использования локального ИИ необходимо установить LM Studio и запустить сервер с моделью.",
                 font=('Segoe UI', 9), foreground='#64748b', wraplength=400).pack(anchor=tk.W, pady=(10, 0))
        
        # === OpenRouter Tab ===
        openrouter_frame = ttk.Frame(notebook, padding="20")
        notebook.add(openrouter_frame, text="OpenRouter")
        
        # Variables for OpenRouter settings
        enable_openrouter = tk.BooleanVar(value=self.ai_chat.enable_openrouter)
        openrouter_api_key = tk.StringVar(value=self.ai_chat.openrouter_api_key)
        openrouter_model = tk.StringVar(value=self.ai_chat.openrouter_model)
        
        ttk.Label(openrouter_frame, text="OpenRouter", font=('Segoe UI', 14, 'bold'), 
                 background='#f8fafc').pack(pady=(0, 15))
        
        # Enable OpenRouter checkbox
        ttk.Checkbutton(openrouter_frame, text="Включить OpenRouter", variable=enable_openrouter).pack(anchor=tk.W)
        
        # API Key entry
        or_api_frame = ttk.LabelFrame(openrouter_frame, text="API ключ OpenRouter", padding="10")
        or_api_frame.pack(fill=tk.X, pady=10)
        
        or_api_entry = ttk.Entry(or_api_frame, textvariable=openrouter_api_key, show="*", width=40)
        or_api_entry.pack(fill=tk.X)
        ttk.Label(or_api_frame, text="Получите API ключ на https://openrouter.ai", 
                 font=('Segoe UI', 9), foreground='#64748b').pack(anchor=tk.W, pady=(5, 0))
        
        # Model selection
        or_model_frame = ttk.LabelFrame(openrouter_frame, text="Модель OpenRouter", padding="10")
        or_model_frame.pack(fill=tk.X, pady=10)
        
        or_model_combo = ttk.Combobox(or_model_frame, textvariable=openrouter_model, 
                                     values=["openai/gpt-3.5-turbo", "openai/gpt-4", "openai/gpt-4-turbo", 
                                            "anthropic/claude-3-haiku", "anthropic/claude-3-sonnet", 
                                            "google/gemini-pro", "meta-llama/llama-3-8b-instruct", 
                                            "mistralai/mistral-7b-instruct", "other"],
                                     state="readonly", width=37)
        or_model_combo.pack(fill=tk.X)
        
        # Добавляем tooltip для OpenRouter модели
        or_model_tooltip = create_tooltip(or_model_combo,
            "Выберите модель OpenRouter:\n\n"
            "• openai/gpt-3.5-turbo - Быстрая и экономичная модель OpenAI\n"
            "• openai/gpt-4 - Более мощная модель OpenAI\n"
            "• openai/gpt-4-turbo - Самая современная модель OpenAI\n"
            "• anthropic/claude-3-haiku - Быстрая модель Anthropic\n"
            "• anthropic/claude-3-sonnet - Сбалансированная модель Anthropic\n"
            "• google/gemini-pro - Модель Google\n"
            "• meta-llama/llama-3-8b-instruct - Модель Meta\n"
            "• mistralai/mistral-7b-instruct - Модель Mistral AI\n"
            "• other - Другая модель из каталога OpenRouter\n\n"
            "Преимущества OpenRouter:\n"
            "• Доступ к 400+ моделям через единый API\n"
            "• Конкуренция цен между провайдерами\n"
            "• Автоматическое распределение нагрузки\n"
            "• Отказоустойчивость")
        
        ttk.Label(openrouter_frame, text="Примечание: OpenRouter предоставляет доступ к более чем 400 моделям ИИ через единый API.",
                 font=('Segoe UI', 9), foreground='#64748b', wraplength=400).pack(anchor=tk.W, pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(settings_window, padding="10")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_settings():
            """Save AI chat settings"""
            settings = {
                'enable_external_ai': enable_external_ai.get(),
                'external_ai_api_key': external_api_key.get(),
                'external_ai_model': external_model.get(),
                'external_ai_base_url': external_base_url.get(),
                'enable_local_ai': enable_local_ai.get(),
                'local_ai_model': local_model.get(),
                'local_ai_base_url': local_base_url.get(),
                'enable_openrouter': enable_openrouter.get(),
                'openrouter_api_key': openrouter_api_key.get(),
                'openrouter_model': openrouter_model.get()
            }
            self.ai_chat.update_settings(settings)
            settings_window.destroy()
            self.update_status("Настройки ИИ сохранены")
        
        ttk.Button(button_frame, text="Сохранить", command=save_settings, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Отмена", 
                  command=settings_window.destroy, 
                  style='Secondary.TButton').pack(side=tk.RIGHT)
    
    def show_system_settings(self):
        """Show comprehensive system settings dialog"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки системы")
        settings_window.geometry("600x700")
        settings_window.resizable(True, True)
        settings_window.configure(bg='#f8fafc')
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === General Settings Tab ===
        general_frame = ttk.Frame(notebook, padding="20")
        notebook.add(general_frame, text="Общие")
        
        # Model settings
        model_frame = ttk.LabelFrame(general_frame, text="Настройки расчетов", padding="15")
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Model type
        ttk.Label(model_frame, text="Тип модели:").pack(anchor=tk.W)
        model_type = tk.StringVar(value=self.settings_manager.get_setting('model_type', 'exponential'))
        model_combo = ttk.Combobox(model_frame, textvariable=model_type,
                                  values=["exponential", "linear", "polynomial"],
                                  state="readonly", width=30)
        model_combo.pack(fill=tk.X, pady=(5, 10))
        
        # Default period
        ttk.Label(model_frame, text="Период по умолчанию (дней):").pack(anchor=tk.W)
        default_period = tk.IntVar(value=self.settings_manager.get_setting('default_period', 7))
        period_spin = ttk.Spinbox(model_frame, from_=1, to=365, textvariable=default_period, width=30)
        period_spin.pack(fill=tk.X, pady=(5, 10))
        
        # Min accuracy
        ttk.Label(model_frame, text="Минимальная точность (%):").pack(anchor=tk.W)
        min_accuracy = tk.DoubleVar(value=self.settings_manager.get_setting('min_accuracy', 50.0))
        accuracy_scale = ttk.Scale(model_frame, from_=0, to=100, variable=min_accuracy, orient=tk.HORIZONTAL)
        accuracy_scale.pack(fill=tk.X, pady=(5, 0))
        accuracy_value = ttk.Label(model_frame, text=f"{min_accuracy.get():.1f}%")
        accuracy_value.pack(anchor=tk.E)
        
        def update_accuracy_label(val):
            accuracy_value.config(text=f"{float(val):.1f}%")
        accuracy_scale.config(command=update_accuracy_label)
        
        # Use adaptive model
        use_adaptive_model = tk.BooleanVar(value=self.settings_manager.get_setting('use_adaptive_model', False))
        ttk.Checkbutton(model_frame, text="Использовать адаптивную модель", 
                       variable=use_adaptive_model).pack(anchor=tk.W, pady=(10, 0))
        
        # Average surplus rate
        ttk.Label(model_frame, text="Средний процент излишка (%):").pack(anchor=tk.W, pady=(10, 0))
        avg_surplus_rate = tk.DoubleVar(value=self.settings_manager.get_setting('average_surplus_rate', 0.0) * 100)
        surplus_scale = ttk.Scale(model_frame, from_=0, to=20, variable=avg_surplus_rate, orient=tk.HORIZONTAL)
        surplus_scale.pack(fill=tk.X, pady=(5, 0))
        surplus_value = ttk.Label(model_frame, text=f"{avg_surplus_rate.get():.1f}%")
        surplus_value.pack(anchor=tk.E)
        
        def update_surplus_label(val):
            surplus_value.config(text=f"{float(val):.1f}%")
        surplus_scale.config(command=update_surplus_label)
        
        # === Interface Settings Tab ===
        interface_frame = ttk.Frame(notebook, padding="20")
        notebook.add(interface_frame, text="Интерфейс")
        
        # Theme settings
        theme_frame = ttk.LabelFrame(interface_frame, text="Тема интерфейса", padding="15")
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        theme = tk.StringVar(value=self.settings_manager.get_setting('theme', 'light'))
        ttk.Radiobutton(theme_frame, text="Светлая", variable=theme, value="light").pack(anchor=tk.W)
        ttk.Radiobutton(theme_frame, text="Темная", variable=theme, value="dark").pack(anchor=tk.W)
        ttk.Radiobutton(theme_frame, text="Системная", variable=theme, value="system").pack(anchor=tk.W)
        
        # Language settings
        lang_frame = ttk.LabelFrame(interface_frame, text="Язык", padding="15")
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        
        language = tk.StringVar(value=self.settings_manager.get_setting('language', 'ru'))
        ttk.Radiobutton(lang_frame, text="Русский", variable=language, value="ru").pack(anchor=tk.W)
        ttk.Radiobutton(lang_frame, text="English", variable=language, value="en").pack(anchor=tk.W)
        
        # Window size
        window_frame = ttk.LabelFrame(interface_frame, text="Размер окна", padding="15")
        window_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(window_frame, text="Ширина:").pack(anchor=tk.W)
        window_width = tk.IntVar(value=self.settings_manager.get_setting('window_width', 1100))
        width_spin = ttk.Spinbox(window_frame, from_=800, to=2000, textvariable=window_width, width=30)
        width_spin.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(window_frame, text="Высота:").pack(anchor=tk.W)
        window_height = tk.IntVar(value=self.settings_manager.get_setting('window_height', 750))
        height_spin = ttk.Spinbox(window_frame, from_=600, to=1500, textvariable=window_height, width=30)
        height_spin.pack(fill=tk.X, pady=(5, 0))
        
        # === Database Settings Tab ===
        database_frame = ttk.Frame(notebook, padding="20")
        notebook.add(database_frame, text="База данных")
        
        # Enable database
        enable_database = tk.BooleanVar(value=self.settings_manager.get_setting('enable_database', True))
        ttk.Checkbutton(database_frame, text="Включить базу данных", 
                       variable=enable_database).pack(anchor=tk.W)
        
        # Database URL
        ttk.Label(database_frame, text="URL базы данных:").pack(anchor=tk.W, pady=(10, 0))
        database_url = tk.StringVar(value=self.settings_manager.get_setting('database_url', 'sqlite:///shrinkage_database.db'))
        url_entry = ttk.Entry(database_frame, textvariable=database_url, width=50)
        url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Backup settings
        backup_frame = ttk.LabelFrame(database_frame, text="Резервное копирование", padding="15")
        backup_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(backup_frame, text="Путь к резервным копиям:").pack(anchor=tk.W)
        backup_path = tk.StringVar(value=self.settings_manager.get_setting('database_backup_path', 'backups/'))
        backup_entry = ttk.Entry(backup_frame, textvariable=backup_path, width=50)
        backup_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(backup_frame, text="Интервал резервного копирования (часы):").pack(anchor=tk.W)
        backup_interval = tk.IntVar(value=self.settings_manager.get_setting('database_backup_interval', 24))
        interval_spin = ttk.Spinbox(backup_frame, from_=1, to=168, textvariable=backup_interval, width=30)
        interval_spin.pack(fill=tk.X, pady=(5, 0))
        
        # Enable verification
        enable_verification = tk.BooleanVar(value=self.settings_manager.get_setting('enable_verification', False))
        ttk.Checkbutton(database_frame, text="Включить верификацию коэффициентов", 
                       variable=enable_verification, pady=(15, 0)).pack(anchor=tk.W)
        
        # === Output Settings Tab ===
        output_frame = ttk.Frame(notebook, padding="20")
        notebook.add(output_frame, text="Вывод")
        
        # Output directory
        ttk.Label(output_frame, text="Директория для результатов:").pack(anchor=tk.W)
        output_dir = tk.StringVar(value=self.settings_manager.get_setting('output_dir', 'результаты'))
        dir_entry = ttk.Entry(output_frame, textvariable=output_dir, width=50)
        dir_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Auto open reports
        auto_open_reports = tk.BooleanVar(value=self.settings_manager.get_setting('auto_open_reports', True))
        ttk.Checkbutton(output_frame, text="Автоматически открывать отчеты", 
                       variable=auto_open_reports).pack(anchor=tk.W)
        
        # Report theme
        ttk.Label(output_frame, text="Тема отчетов:").pack(anchor=tk.W, pady=(10, 0))
        report_theme = tk.StringVar(value=self.settings_manager.get_setting('report_theme', 'default'))
        theme_combo = ttk.Combobox(output_frame, textvariable=report_theme,
                                  values=["default", "dark", "light", "colorful"],
                                  state="readonly", width=30)
        theme_combo.pack(fill=tk.X, pady=(5, 0))
        
        # === Buttons ===
        button_frame = ttk.Frame(settings_window, padding="10")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_settings():
            """Save all system settings"""
            # Update settings
            new_settings = {
                'model_type': model_type.get(),
                'default_period': default_period.get(),
                'min_accuracy': min_accuracy.get(),
                'use_adaptive_model': use_adaptive_model.get(),
                'average_surplus_rate': avg_surplus_rate.get() / 100.0,  # Convert from percentage
                'theme': theme.get(),
                'language': language.get(),
                'window_width': window_width.get(),
                'window_height': window_height.get(),
                'enable_database': enable_database.get(),
                'database_url': database_url.get(),
                'database_backup_path': backup_path.get(),
                'database_backup_interval': backup_interval.get(),
                'enable_verification': enable_verification.get(),
                'output_dir': output_dir.get(),
                'auto_open_reports': auto_open_reports.get(),
                'report_theme': report_theme.get()
            }
            
            # Update settings manager
            self.settings_manager.update_settings(new_settings)
            self.settings_manager.save_settings()
            
            # Update UI variables
            self.use_adaptive.set(use_adaptive_model.get())
            
            # Update window size
            self.root.geometry(f"{window_width.get()}x{window_height.get()}")
            
            settings_window.destroy()
            self.update_status("Системные настройки сохранены")
        
        def reset_to_defaults():
            """Reset all settings to defaults"""
            if messagebox.askyesno("Сброс настроек", "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?"):
                self.settings_manager.reset_to_defaults()
                settings_window.destroy()
                self.update_status("Настройки сброшены к значениям по умолчанию")
                messagebox.showinfo("Сброс настроек", "Настройки сброшены к значениям по умолчанию. Перезапустите приложение для применения изменений.")
        
        ttk.Button(button_frame, text="Сбросить", command=reset_to_defaults,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Отмена", 
                  command=settings_window.destroy,
                  style='Secondary.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Сохранить", command=save_settings,
                  style='Accent.TButton').pack(side=tk.RIGHT)


def main():
    root = tk.Tk()
    app = ShrinkageCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()