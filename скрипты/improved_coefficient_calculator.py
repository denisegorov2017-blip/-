import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List, Dict, Tuple, Optional, Union
import warnings
import json
import concurrent.futures
from analytics import forecast_shrinkage, compare_coefficients, cluster_nomenclatures
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)

# Конфигурационные параметры
CONFIG = {
    'default_period_days': 7,
    'default_b_coef': 0.049,
    'max_workers': 4,
    'cache_size': 128
}

def setup_logging(project_root):
    """Настраивает систему логирования."""
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Основной логгер для информации
    info_logger = logging.getLogger('info_logger')
    info_logger.setLevel(logging.INFO)
    info_handler = TimedRotatingFileHandler(os.path.join(log_dir, 'info.log'), when='D', interval=1, backupCount=7, encoding='utf-8')
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    info_logger.addHandler(info_handler)

    # Логгер для ошибок
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler(os.path.join(log_dir, 'errors.log'), encoding='utf-8')
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    error_logger.addHandler(error_handler)

    return info_logger, error_logger

def parse_inventory_data_improved(csv_file: str, target_balance_date: Optional[datetime] = None) -> Tuple[List[Dict], List[str]]:
    """
    Улучшенный парсинг данных из CSV файла с разделением на товары и группы.
    Может извлекать остатки на заданную дату, если указана target_balance_date.
    
    Args:
        csv_file: Путь к CSV файлу с данными
        target_balance_date: Дата, на которую нужно извлечь начальные остатки
        
    Returns:
        Кортеж из:
        - Список словарей с данными по номенклатуре
        - Список названий групп товаров
        
    Raises:
        ValueError: Если файл не существует или имеет неверный формат
    """
    if not os.path.exists(csv_file):
        raise ValueError(f"Файл {csv_file} не найден")
        
    try:
        df = pd.read_csv(csv_file, header=None, dtype=str)
        if df.empty:
            raise ValueError("Файл CSV пуст")
    except Exception as e:
        raise ValueError(f"Ошибка чтения CSV файла: {str(e)}")
    
    nomenclature_data = []
    group_data = []
    
    # Переменные для отслеживания текущей даты остатков
    current_balance_date = None  # Дата, на которую рассчитаны остатки в текущей секции
    collecting_balances_for_target_date = False  # Флаг сбора остатков для target_balance_date
    
    # Временные хранилища данных
    temp_nomenclature_data = []  # Для сбора всех номенклатур при парсинге по умолчанию
    temp_group_data = []         # Для сбора групп при парсинге по умолчанию
    
    # Хранилище данных для target_balance_date
    balances_for_target_date = {}  # {название_номенклатуры: {summary, documents}}
    
    def save_current_nomenclature(is_collecting_default=False, is_collecting_target=False, 
                                current_nomenclature=None, current_summary=None, current_documents=None):
        """Сохраняет данные по текущей номенклатуре"""
        nonlocal temp_nomenclature_data, temp_group_data, balances_for_target_date
        
        if not current_nomenclature or not current_summary:
            return
            
        nomenclature_entry = {
            'name': current_nomenclature,
            'summary': current_summary,
            'documents': current_documents or []
        }
        
        # Сохраняем для парсинга по умолчанию
        if is_collecting_default:
            if not current_documents:
                temp_group_data.append(current_nomenclature)
            else:
                temp_nomenclature_data.append(nomenclature_entry)
        
        # Сохраняем для target_balance_date
        if is_collecting_target:
            if not current_documents:
                # Группы не сохраняем, так как для расчета коэффициентов нужны конкретные номенклатуры с документами
                pass
            else:
                balances_for_target_date[current_nomenclature] = nomenclature_entry

    # Инициализация переменных для текущей номенклатуры
    current_nomenclature = None
    current_summary = None
    current_documents = []
    
    # Проходим по всем строкам файла
    for idx, row in df.iterrows():
        row_str = str(row[0]) if pd.notna(row[0]) else ""
        
        # Проверка на строку с номенклатурой (заголовок раздела)
        is_new_nomenclature = (
            re.match(r'^[А-ЯЁ\s\(\)\"\/\.]+$', row_str.strip()) and 
            len(row_str.strip()) > 3 and 
            pd.isna(row[1])
        )

        # Проверка на строку Инвентаризации
        inventory_match = re.search(r'Инвентаризация.*?от (\d{2})\.(\d{2})\.(\d{4})', row_str)
        if inventory_match:
            day_inv, month_inv, year_inv = inventory_match.groups()
            try:
                inventory_datetime = datetime(int(year_inv), int(month_inv), int(day_inv))
                # Остатки после инвентаризации считаются относящимися к следующему дню
                current_balance_date = inventory_datetime + timedelta(days=1)
                print(f"Найдена инвентаризация на {inventory_datetime.strftime('%d.%m.%Y')}, остатки на {current_balance_date.strftime('%d.%m.%Y')}")
            except ValueError:
                pass  # Неверный формат даты

        # Проверка на начало периода отчета (резервный вариант)
        if not current_balance_date and idx > 10 and "Параметры:" in row_str and "Период:" in row_str:
             # Извлечь дату начала периода из строки "Параметры: Период: 15.07.2025 - 21.07.2025"
             period_match = re.search(r'Период:\s*(\d{2})\.(\d{2})\.(\d{4})', row_str)
             if period_match:
                 day_p, month_p, year_p = period_match.groups()
                 try:
                     current_balance_date = datetime(int(year_p), int(month_p), int(day_p))
                     print(f"Найден период отчета, остатки на {current_balance_date.strftime('%d.%m.%Y')}")
                 except ValueError:
                     pass

        # Определяем, нужно ли собирать остатки из текущей секции
        if target_balance_date and current_balance_date:
            collecting_balances_for_target_date = (
                current_balance_date.date() == target_balance_date.date()
            )
        else:
            collecting_balances_for_target_date = False
            
        # Сбор остатков по умолчанию (как в оригинальной функции)
        collecting_by_default = (target_balance_date is None)
        
        # Если это новая номенклатура
        if is_new_nomenclature:
            # Сохраняем предыдущую номенклатуру
            save_current_nomenclature(
                is_collecting_default=collecting_by_default,
                is_collecting_target=collecting_balances_for_target_date,
                current_nomenclature=current_nomenclature,
                current_summary=current_summary,
                current_documents=current_documents
            )
            
            # Начинаем новую номенклатуру
            current_nomenclature = row_str.strip()
            current_summary = None
            current_documents = []
            
            # Ищем строку с остатками (в следующих 15 строках)
            for i in range(idx + 1, min(idx + 15, len(df))):
                next_row = df.iloc[i]
                if pd.notna(next_row[4]) and pd.notna(next_row[8]):
                    try:
                        initial = float(str(next_row[4]).replace(',', '.'))
                        income = float(str(next_row[6]).replace(',', '.')) if pd.notna(next_row[6]) else 0
                        expense = float(str(next_row[7]).replace(',', '.')) if pd.notna(next_row[7]) else 0
                        final = float(str(next_row[8]).replace(',', '.'))
                        
                        current_summary = {
                            'initial': initial,
                            'income': income,
                            'expense': expense,
                            'final': final
                        }
                        break
                    except:
                        continue
                        
        # Если у нас есть текущая номенклатура и строка не пустая
        elif current_nomenclature and row_str.strip():
            # Проверяем, является ли строка документом
            if any(keyword in row_str for keyword in [
                'Отчет отдела', 'Приходная накладная', 'Инвентаризация', 
                'Списание', 'Перемещение', 'Пересортица'
            ]):
                current_documents.append({
                    'name': row_str.strip(),
                    'data': []
                })
            # Проверяем, является ли строка датой партии
            elif re.match(r'\d{2}\.\d{2}\.\d{4}', row_str.strip()):
                if current_documents:
                    try:
                        values = []
                        for col in range(4, 9):
                            val_str = str(row[col]).replace(',', '.') if pd.notna(row[col]) and str(row[col]).strip() != '' else '0'
                            try:
                                values.append(float(val_str))
                            except (ValueError, IndexError):
                                values.append(0)
                        
                        current_documents[-1]['data'].append({
                            'date': row_str.strip(),
                            'values': values
                        })
                    except:
                        continue
    
    # Сохраняем последнюю номенклатуру
    save_current_nomenclature(
        is_collecting_default=collecting_by_default,
        is_collecting_target=collecting_balances_for_target_date,
        current_nomenclature=current_nomenclature,
        current_summary=current_summary,
        current_documents=current_documents
    )
    
    # Возвращаем результаты в зависимости от режима
    if target_balance_date:
        # Возвращаем данные, собранные для target_balance_date
        print(f"Возвращаем данные для остатков на {target_balance_date.strftime('%d.%m.%Y')}")
        return list(balances_for_target_date.values()), []
    else:
        # Возвращаем данные, собранные по умолчанию
        print("Возвращаем данные по умолчанию")
        return temp_nomenclature_data, temp_group_data

def calculate_coefficients_improved(
    nomenclature_data: Dict, 
    period_days: int = CONFIG['default_period_days'],
    b_coef: float = CONFIG['default_b_coef']
) -> Tuple[Optional[Dict], str, Optional[float]]:
    # Прямой вызов реализации без кэширования, чтобы избежать проблем с хэшируемостью
    return _calculate_impl(nomenclature_data, period_days, b_coef)

def _calculate_impl(
    nomenclature_data: Dict,
    period_days: int,
    b_coef: float
) -> Tuple[Optional[Dict], str, Optional[float]]:
    # Данные уже восстановлены из JSON
    """
    Расчет коэффициентов усушки с улучшенной обработкой ошибок и поддержкой разных периодов.
    
    Args:
        nomenclature_data: Данные по номенклатуре
        period_days: Количество дней в периоде (по умолчанию 7)
        b_coef: Коэффициент b (по умолчанию 0.049)
        
    Returns:
        Кортеж из:
        - Словарь с результатами или None при ошибке
        - Строка с причиной (успех или описание ошибки)
        - Вес отклонения или None
    """
    try:
        name = nomenclature_data['name']
        summary = nomenclature_data['summary']
        documents = nomenclature_data['documents']
        
        if not summary:
            return None, "Нет данных об остатках", None
            
        initial_mass = summary['initial']
        income = summary['income']
        expense = summary['expense']
        final_mass_by_accounting = summary['final']
        
        if initial_mass <= 0:
            return None, f"Нулевой или отрицательный начальный остаток ({initial_mass:.3f} кг)", None
            
        if income < 0:
            return None, f"Отрицательный приход ({income:.3f} кг)", None
            
        if expense < 0:
            return None, f"Отрицательный расход ({expense:.3f} кг)", None
            
        if final_mass_by_accounting < 0:
            return None, f"Отрицательный конечный остаток по учету ({final_mass_by_accounting:.3f} кг)", None
            
        # Расчет фактической усушки
        actual_shrinkage = initial_mass + income - expense - final_mass_by_accounting
        
        if actual_shrinkage <= 0.005:
            if actual_shrinkage <= 0:
                return None, f"Излишек по инвентаризации", None
            else:
                return None, f"Незначительная усушка", None
                
        # Подготовка данных для расчета
        inventory_shrinkage = None
        failure_reason = "Не найдено подходящих данных по инвентаризации"
        deviation_weight = None
        
        # Ищем данные из инвентаризации
        for doc in documents:
            if 'Инвентаризация' in doc['name']:
                doc_date_str = doc['name'].split(' от ')[1].split(' ')[0]
                try:
                    doc_end_date = datetime.strptime(doc_date_str, '%d.%m.%Y')
                    
                    # Ищем последний день с данными
                    last_day_with_data = None
                    last_data = None
                    
                    for day_data in doc['data']:
                        if len(day_data['values']) >= 5:
                            batch_date = datetime.strptime(day_data['date'], '%d.%m.%Y %H:%M:%S')
                            
                            # Проверяем, есть ли значимые изменения массы
                            if abs(day_data['values'][1] - day_data['values'][0]) > 0.001:
                                last_day_with_data = batch_date
                                last_data = day_data['values']
                                
                    if last_day_with_data and last_data:
                        # Рассчитываем вес отклонения (с учетом масштаба)
                        initial_for_deviation = max(initial_mass, 1.0)  
                        deviation_weight = abs((last_data[4] - final_mass_by_accounting) / initial_for_deviation)
                        
                        # Проверяем, что инвентаризация была проведена в конце периода
                        if (doc_end_date - last_day_with_data).days <= 2:
                            inventory_shrinkage = actual_shrinkage
                            failure_reason = "Успех"
                            break
                        else:
                            failure_reason = f"Инвентаризация не в конце периода (последние данные {last_day_with_data.strftime('%d.%m.%Y')})"
                except Exception as e:
                    failure_reason = f"Ошибка обработки данных инвентаризации: {str(e)}"
                    
        if inventory_shrinkage is None:
            return None, failure_reason, deviation_weight
            
        # Дата начала расчета коэффициентов
        report_start_date_str = '15.07.2025'
        report_start_date = datetime.strptime(report_start_date_str, '%d.%m.%Y')

        # Подготовка данных о массе по дням хранения
        daily_masses = []
        current_mass = summary['initial']
        
        for doc in documents:
            for day_data in doc['data']:
                if len(day_data['values']) >= 5:
                    try:
                        batch_date = datetime.strptime(day_data['date'], '%d.%m.%Y %H:%M:%S')
                        if batch_date < report_start_date:
                            days_in_storage = (datetime.strptime(doc['name'].split(' от ')[1].split(' ')[0], '%d.%m.%Y') - report_start_date).days
                        else:
                            days_in_storage = (datetime.strptime(doc['name'].split(' от ')[1].split(' ')[0], '%d.%m.%Y') - batch_date).days
                    except:
                        try:
                            batch_date = datetime.strptime(day_data['date'], '%d.%m.%Y %H:%M')
                            if batch_date < report_start_date:
                                days_in_storage = (datetime.strptime(doc['name'].split(' от ')[1].split(' ')[0], '%d.%m.%Y') - report_start_date).days
                            else:
                                days_in_storage = (datetime.strptime(doc['name'].split(' от ')[1].split(' ')[0], '%d.%m.%Y') - batch_date).days
                        except:
                            continue
                            
                    mass_on_day = day_data['values'][4]  
                    daily_masses.append((days_in_storage, mass_on_day))
                    
        if not daily_masses:
            return None, "Нет данных о распределении массы по дням хранения", None
            
        # Сортировка по возрастанию дней хранения
        daily_masses.sort(key=lambda x: x[0])
        
        # Расчет средневзвешенного срока хранения
        total_mass = sum(mass for _, mass in daily_masses)
        if total_mass <= 0:
            return None, "Нулевая или отрицательная общая масса для расчета срока хранения", None
            
        weighted_avg_storage_time = sum(days * mass for days, mass in daily_masses) / total_mass
        
        # Проверка корректности срока хранения
        if weighted_avg_storage_time < 0 or weighted_avg_storage_time > 365:
            return None, f"Некорректный средневзвешенный срок хранения ({weighted_avg_storage_time:.2f} дней)", None
            
        # Расчет коэффициентов
        try:
            k = inventory_shrinkage / initial_mass  
            
            if weighted_avg_storage_time <= 0:
                return None, f"Некорректный срок хранения ({weighted_avg_storage_time:.2f} дней) для расчета коэффициентов", None
                
            # Расчет коэффициентов модели a * exp(-b * t) + c * t
            a = k * np.exp(b_coef * weighted_avg_storage_time) / (1 - np.exp(-b_coef * weighted_avg_storage_time))
            c = k - a * (1 - np.exp(-b_coef * weighted_avg_storage_time))
            
            # Ограничения на коэффициенты
            a = max(min(a, 1.0), 0.0)
            c = max(min(c, 1.0), -1.0)
            
            # Проверка на вырожденность
            if abs(a) < 1e-10 and abs(c) < 1e-10:
                return None, "Вырожденная модель (нулевые коэффициенты)", None
                
        except Exception as e:
            return None, f"Ошибка расчета коэффициентов: {str(e)}", None
            
        coefficients = {
            'a': round(a, 6),
            'b': round(b_coef, 6),
            'c': round(c, 6)
        }
        
        return coefficients, "Успех", deviation_weight
        
    except Exception as e:
        return None, f"Неизвестная ошибка: {str(e)}", None

def save_coefficients_to_csv(results: List[Dict], output_file: str, failed_items: List[Dict], html_failures_output_file: str):
    """Сохраняет результаты расчета коэффициентов в CSV файл."""
    df = pd.DataFrame(results)
    
    columns_order = ['Номенклатура', 'a', 'b (день⁻¹)', 'c', 'Примечание']
    df = df.reindex(columns=columns_order)
    
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Результаты расчета коэффициентов сохранены в файл: {output_file}")

def save_coefficients_to_html(results: List[Dict], output_file: str):
    """Сохраняет результаты расчета коэффициентов в HTML файл."""
    df = pd.DataFrame(results)
    
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Результаты расчета коэффициентов усушки</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) {background-color: #f9f9f9;}
        tr:hover {background-color: #f5f5f5;}
        .footer { margin-top: 20px; font-style: italic; color: #666; }
    </style>
</head>
<body>
    <h2>Результаты расчета коэффициентов усушки</h2>
    {}
    <div class="footer">Коэффициенты рассчитаны с использованием модели a * exp(-b * t) + c * t<br>
    b зафиксирован на уровне 0.049 день⁻¹</div>
</body>
</html>
'''
    
    html_table = df.to_html(index=False, table_id="coefficients-table")
    html_result = html_template.format(html_table)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_result)
    print(f"Результаты расчета коэффициентов сохранены в файл: {output_file}")

def save_failures_to_html(group_data: List[str], failed_items: List[Dict], output_file: str):
    """Сохраняет список необработанных позиций в HTML файл."""
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Необработанные позиции</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; cursor: pointer; }
        th:hover { background-color: #ddd; }
        tr:nth-child(even) {background-color: #f9f9f9;}
        tr:hover {background-color: #f5f5f5;}
        .sort-asc::after { content: ' ▲'; }
        .sort-desc::after { content: ' ▼'; }
    </style>
</head>
<body>
    <h2>Пропущенные группы товаров</h2>
    <table id="skipped-table">
        <thead>
            <tr><th>#</th><th>Название группы</th></tr>
        </thead>
        <tbody>
            {}
        </tbody>
    </table>

    <h2 style="margin-top: 40px;">Номенклатуры, по которым не удалось рассчитать коэффициенты</h2>
    <table id="failed-table">
        <thead>
            <tr><th>#</th><th>Номенклатура</th><th>Причина</th><th>Вес отклонения</th></tr>
        </thead>
        <tbody>
            {}
        </tbody>
    </table>

    <script>
function sortTable(table, columnIndex, asc = true) {
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    const sortedRows = rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();

        let comparison = 0;
        const aNum = parseFloat(aText.replace(",", "."));
        const bNum = parseFloat(bText.replace(",", "."));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            comparison = aNum - bNum;
        } else {
            comparison = aText.localeCompare(bText);
        }

        return asc ? comparison : -comparison;
    });

    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    tbody.append(...sortedRows);

    table.querySelectorAll("thead th").forEach(th => th.classList.remove("sort-asc", "sort-desc"));
    const headerCell = table.querySelector(`thead th:nth-child(${columnIndex + 1})`);
    if (headerCell) {
        headerCell.classList.toggle("sort-asc", asc);
        headerCell.classList.toggle("sort-desc", !asc);
    }
}

document.querySelectorAll("#failed-table thead th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAsc = headerCell.classList.contains("sort-asc");

        sortTable(tableElement, headerIndex, !currentIsAsc);
    });
});
    </script>
</body>
</html>
'''
    
    skipped_html = ""
    for i, group in enumerate(group_data, 1):
        skipped_html += f"<tr><td>{i}</td><td>{group}</td></tr>"

    failed_html = ""
    for i, item in enumerate(failed_items, 1):
        weight_str = f"{-item['weight']:.3f}" if item['weight'] is not None and item['weight'] <= 0 else (
            f"{item['weight']:.3f}" if item['weight'] is not None else "н/д"
        )
        failed_html += f"<tr><td>{i}</td><td>{item['name']}</td><td>{item['reason']}</td><td>{weight_str}</td></tr>"

    final_html = html_template.format(skipped_html, failed_html)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

def main():
    """
    Основная функция для расчета коэффициентов с улучшенной обработкой ошибок.
    
    Логирует прогресс и ошибки в файлы журналов.
    """
    try:
        import argparse
        
        parser = argparse.ArgumentParser(description="Расчет коэффициентов усушки")
        parser.add_argument('--calculation_start_date', type=str, help='Дата начала расчета (ГГГГ-ММ-ДД)')
        args = parser.parse_args()
        
        target_balance_date = None
        if args.calculation_start_date:
            try:
                target_balance_date = datetime.strptime(args.calculation_start_date, "%Y-%m-%d")
                print(f"Будет использован остаток на утро {args.calculation_start_date}")
            except ValueError:
                print(f"Неверный формат даты: {args.calculation_start_date}. Используется остаток по умолчанию.")
                
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Настройка логирования
        info_logger, error_logger = setup_logging(project_root)
        info_logger.info("Запуск расчета коэффициентов усушки")
        
        csv_file = os.path.join(project_root, "исходные_данные", "sheet_1_Лист_1.csv")
        csv_output_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
        html_output_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.html")
        html_failures_output_file = os.path.join(project_root, "результаты", "необработанные_позиции.html")
        
        info_logger.info(f"Начинаю анализ данных из файла: {csv_file}")
        print(f"Начинаю улучшенный анализ данных...\nИсходный файл: {csv_file}")
        
        nomenclature_data, group_data = parse_inventory_data_improved(csv_file, target_balance_date)
        print(f"Найдено номенклатур для расчета: {len(nomenclature_data)}")
        print(f"Найдено групп: {len(group_data)}")
        
        # Удаление дубликатов из nomenclature_data
        unique_nomenclature_data = []
        seen_names = set()
        for item in nomenclature_data:
            if item['name'] not in seen_names:
                unique_nomenclature_data.append(item)
                seen_names.add(item['name'])
            else:
                print(f"Найден дубликат номенклатуры: {item['name']}. Пропускаем.")
        
        nomenclature_data = unique_nomenclature_data
        print(f"Уникальных номенклатур для расчета после удаления дубликатов: {len(nomenclature_data)}")
        
        results = []
        failed_items = []

        # Многопоточная обработка номенклатур
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as executor:
            futures = []
            # Создаем словарь для сопоставления фьючерсов с номенклатурами
            future_to_nomenclature = {}
            for nomenclature in nomenclature_data:
                future = executor.submit(
                    calculate_coefficients_improved, 
                    nomenclature
                )
                futures.append(future)
                future_to_nomenclature[future] = nomenclature
            
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                nomenclature = future_to_nomenclature[future]
                coefficients, reason, weight = future.result()
                if coefficients:
                    results.append({
                        'Номенклатура': nomenclature['name'],
                        'a': coefficients['a'],
                        'b (день⁻¹)': coefficients['b'],
                        'c': coefficients['c'],
                        'Примечание': f"Расчет по данным за период 15.07.25-21.07.25. Усушка {nomenclature['summary']['initial'] + nomenclature['summary']['income'] - nomenclature['summary']['expense'] - nomenclature['summary']['final']:.3f} кг за {7} дней хранения."
                    })
                    info_logger.info(f"[{i}/{len(nomenclature_data)}] Рассчитаны коэффициенты для '{nomenclature['name']}': a={coefficients['a']:.6f}, b={coefficients['b']:.6f}, c={coefficients['c']:.6f}")
                else:
                    failed_items.append({
                        'name': nomenclature['name'],
                        'reason': reason,
                        'weight': weight
                    })
                    error_logger.error(f"[{i}/{len(nomenclature_data)}] Не удалось рассчитать коэффициенты для '{nomenclature['name']}': {reason}")
                    
                if i % 10 == 0 or i == len(nomenclature_data):
                    print(f"Обработано: {i}/{len(nomenclature_data)} номенклатур")
        
        print("\nСохранение результатов...")
        if results:
            save_coefficients_to_csv(results, csv_output_file, failed_items, html_failures_output_file)
            save_coefficients_to_html(results, html_output_file)
            
            df_results = pd.DataFrame(results)
            print("\nТоп-20 рассчитанных коэффициентов:")
            for i, (_, row) in enumerate(df_results.head(20).iterrows(), 1):
                print(f"{i:2d}. {row['Номенклатура']}: a={row['a']:.6f}, b={row['b (день⁻¹)']:.6f}, c={row['c']:.6f}")
        else:
            print("Не удалось рассчитать коэффициенты ни для одной номенклатуры")
            
        if failed_items or group_data:
            save_failures_to_html(group_data, failed_items, html_failures_output_file)
            print(f"\nСписок необработанных позиций сохранен в файл: {html_failures_output_file}")
            
        info_logger.info(f"Расчет завершен. Успешно: {len(results)}, Ошибок: {len(failed_items)}, Групп: {len(group_data)}")
        print(f"\nРасчет завершен. Успешно: {len(results)}, Ошибок: {len(failed_items)}, Групп: {len(group_data)}")
        
    except Exception as e:
        print(f"Произошла критическая ошибка: {str(e)}")
        if 'error_logger' in locals():
            error_logger.error(f"Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()