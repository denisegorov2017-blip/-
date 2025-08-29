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
from src.logger_config import log


class ShrinkageCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Система Расчета Коэффициентов Усушки")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        
        # Initialize AI Chat
        self.ai_chat = AIChat()
        
        # Configure modern styles
        self.setup_styles()
        
        # Variables
        self.file_path = tk.StringVar()
        self.use_adaptive = tk.BooleanVar(value=False)
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
        settings_window.geometry("400x350")
        settings_window.resizable(False, False)
        settings_window.configure(bg='#f8fafc')
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Variables for settings
        enable_external_ai = tk.BooleanVar(value=self.ai_chat.enable_external_ai)
        api_key = tk.StringVar(value=self.ai_chat.external_ai_api_key)
        model = tk.StringVar(value=self.ai_chat.external_ai_model)
        base_url = tk.StringVar(value=self.ai_chat.external_ai_base_url)
        
        # Create widgets
        ttk.Label(settings_window, text="Настройки ИИ-чата", font=('Segoe UI', 14, 'bold'), 
                 background='#f8fafc').pack(pady=(20, 15))
        
        # Enable external AI checkbox
        enable_frame = ttk.Frame(settings_window, padding="10", style='TLabelframe')
        enable_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Checkbutton(enable_frame, text="Включить внешний ИИ", variable=enable_external_ai).pack(anchor=tk.W)
        
        # API Key entry
        api_frame = ttk.Frame(settings_window, padding="10", style='TLabelframe')
        api_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(api_frame, text="API ключ:").pack(anchor=tk.W)
        api_entry = ttk.Entry(api_frame, textvariable=api_key, show="*", width=40)
        api_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Base URL entry
        url_frame = ttk.Frame(settings_window, padding="10", style='TLabelframe')
        url_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(url_frame, text="Базовый URL:").pack(anchor=tk.W)
        url_entry = ttk.Entry(url_frame, textvariable=base_url, width=40)
        url_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Model selection
        model_frame = ttk.Frame(settings_window, padding="10", style='TLabelframe')
        model_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(model_frame, text="Модель ИИ:").pack(anchor=tk.W)
        model_combo = ttk.Combobox(model_frame, textvariable=model, 
                                  values=["gpt-3.5-turbo", "gpt-4", "claude-3", "other"],
                                  state="readonly", width=37)
        model_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Note
        note_frame = ttk.Frame(settings_window, padding="10", style='TLabelframe')
        note_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(note_frame, text="Примечание: Для использования внешних ИИ сервисов необходимо иметь действующий API ключ.",
                 font=('Segoe UI', 9), foreground='#64748b', wraplength=350).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(settings_window, padding="10")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_settings():
            """Save AI chat settings"""
            settings = {
                'enable_external_ai': enable_external_ai.get(),
                'external_ai_api_key': api_key.get(),
                'external_ai_model': model.get(),
                'external_ai_base_url': base_url.get()
            }
            self.ai_chat.update_settings(settings)
            settings_window.destroy()
            self.update_status("Настройки ИИ сохранены")
        
        ttk.Button(button_frame, text="Сохранить", command=save_settings, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Отмена", 
                  command=settings_window.destroy, 
                  style='Secondary.TButton').pack(side=tk.RIGHT)


def main():
    root = tk.Tk()
    app = ShrinkageCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()