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
from functools import wraps

# Подавляем предупреждения от pandas о типах данных
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


def parse_inventory_data_improved(csv_file: str) -> Tuple[List[Dict], List[str]]:
    """
    Улучшенный парсинг данных из CSV файла с разделением на товары и группы.
    
    Args:
        csv_file: Путь к CSV файлу с данными
        
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
    current_nomenclature = None
    current_summary = None
    current_documents = []

    def save_current_nomenclature():
        nonlocal current_nomenclature, current_summary, current_documents, nomenclature_data, group_data
        if current_nomenclature and current_summary:
            if not current_documents:
                group_data.append(current_nomenclature)
            else:
                nomenclature_data.append({
                    'name': current_nomenclature,
                    'summary': current_summary,
                    'documents': current_documents
                })

    for idx, row in df.iterrows():
        row_str = str(row[0]) if pd.notna(row[0]) else ""
        
        is_new_nomenclature = re.match(r'^[А-ЯЁ\s\(\)\"\.\/]+$', row_str.strip()) and len(row_str.strip()) > 3 and pd.isna(row[1])

        if is_new_nomenclature:
            save_current_nomenclature()
            
            current_nomenclature = row_str.strip()
            current_summary = None
            current_documents = []
            
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
        
        elif current_nomenclature and row_str.strip():
            if any(keyword in row_str for keyword in ['Отчет отдела', 'Приходная накладная', 'Инвентаризация', 'Списание', 'Перемещение', 'Пересортица']):
                current_documents.append({
                    'name': row_str.strip(),
                    'data': []
                })
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
    
    save_current_nomenclature()
    
    return nomenclature_data, group_data


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
    """
    Расчет коэффициентов усушки с улучшенной обработкой ошибок и поддержкой разных периодов.
    
    Args:
        nomenclature_data: Данные по номенклатуре
        period_days: Количество дней в периоде (по умолчанию 7)
        b_coef: Коэффициент b (по умолчанию 0.049)
        
    Returns:
        Кортеж из:
        - Словарь с результатами или None при ошибке
        - Причина сбоя (или "Успех")
        - Величина отклонения (кг)
    """
    if not nomenclature_data or 'summary' not in nomenclature_data or 'documents' not in nomenclature_data:
        return None, "Неверный формат данных номенклатуры", None
        
    summary = nomenclature_data['summary']
    documents = nomenclature_data['documents']
    
    # Валидация summary
    required_summary_fields = ['initial', 'income', 'expense', 'final']
    if not all(field in summary for field in required_summary_fields):
        return None, "Отсутствуют необходимые поля в summary", None
    
    inventory_shrinkage = None
    deviation_weight = None
    failure_reason = "Данные по инвентаризации отсутствуют"

    for doc in documents:
        if 'Инвентаризация' in doc['name'] and doc['data']:
            total_shrinkage = 0
            for batch_data in doc['data']:
                if len(batch_data['values']) >= 5:
                    theoretical = batch_data['values'][0]
                    actual = batch_data['values'][4]
                    total_shrinkage += (theoretical - actual)
            
            deviation_weight = total_shrinkage
            
            if total_shrinkage > 0.005:
                inventory_shrinkage = total_shrinkage
                failure_reason = "Успех"
                break
            elif total_shrinkage <= 0:
                failure_reason = f"Излишек по инвентаризации"
                break
            else:
                failure_reason = f"Незначительная усушка"
    
    if inventory_shrinkage is None:
        return None, failure_reason, deviation_weight
    
    report_start_date_str = '15.07.2025'
    report_start_date = datetime.strptime(report_start_date_str, '%d.%m.%Y')

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
                    days_in_storage = 1

                if day_data['values'][2] > 0:
                    current_mass += day_data['values'][2]
                if day_data['values'][3] > 0:
                    current_mass -= day_data['values'][3]
                daily_masses.append(current_mass)
    
    if not daily_masses:
        daily_masses = [summary['initial']] * 7
    
    daily_masses = daily_masses[:7]
    while len(daily_masses) < 7:
        daily_masses.append(daily_masses[-1] if daily_masses else 0)
    
    # Расчет коэффициентов с учетом длины периода
    exp_coefficients = [np.exp(-b_coef * day) for day in range(1, period_days + 1)]
    
    # Нормализация daily_masses под длину периода
    daily_masses = daily_masses[:period_days]
    while len(daily_masses) < period_days:
        daily_masses.append(daily_masses[-1] if daily_masses else 0)
    
    S = sum(mass * exp_coeff for mass, exp_coeff in zip(daily_masses, exp_coefficients))
    
    # Расчет коэффициента a с проверкой деления на ноль
    try:
        a = (inventory_shrinkage / (b_coef * S)) if (b_coef * S) > 1e-10 else 0
    except Exception as e:
        logging.error(f"Ошибка расчета коэффициента a: {str(e)}")
        a = 0
    
    if not (0 <= a <= 1):
        return None, f"Расчетный коэффициент 'a' ({round(a,3)}) вне допустимого диапазона [0, 1]", inventory_shrinkage
    
    calculated_shrinkage = a * b_coef * S
    accuracy = (1 - abs(inventory_shrinkage - calculated_shrinkage) / inventory_shrinkage) * 100 if inventory_shrinkage > 0 else 0
    
    return {
        'nomenclature': nomenclature_data['name'],
        'a': round(a, 3),
        'b': b_coef,
        'c': 0,
        'accuracy': round(accuracy, 1),
        'shrinkage': inventory_shrinkage,
        'period': '15.07.25-21.07.25'
    }, "Успех", inventory_shrinkage


def save_to_html(df_results, output_file):
    """Сохраняет результаты в HTML формате с поиском и нумерацией"""
    
    df_with_numbers = df_results.copy()
    df_with_numbers.insert(0, '№', range(1, len(df_with_numbers) + 1))
    
    html_template = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Коэффициенты усушки</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
        .container {{ max-width: 1400px; margin: 20px auto; padding: 10px; }}
        .search-container {{ 
            margin-bottom: 20px; 
            padding: 15px; 
            background: #f0f0f0; 
            border-radius: 5px;
            position: sticky;
            top: 0;
            z-index: 3;
        }}
        .search-input {{ 
            width: 300px; 
            padding: 8px; 
            font-size: 14px; 
            border: 1px solid #ccc; 
            border-radius: 4px;
        }}
        .search-label {{ 
            font-weight: bold; 
            margin-right: 10px; 
        }}
        .table-container {{ 
            max-height: 70vh; 
            overflow-y: auto; 
            border: 1px solid #ccc; 
            border-radius: 5px;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            font-size: 14px; 
        }}
        thead th {{
            position: sticky;
            top: 0;
            background: #4CAF50;
            color: white;
            z-index: 2;
            border-bottom: 2px solid #45a049;
            padding: 12px 8px;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #e8f5e8; }}
        .hidden {{ display: none; }}
        .number-cell {{ 
            background: #f0f0f0; 
            font-weight: bold; 
            text-align: center;
            width: 50px;
        }}
        .stats {{ 
            margin-top: 10px; 
            font-size: 12px; 
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Коэффициенты усушки (автоматический расчет)</h2>
        
        <div class="search-container">
            <label class="search-label">Поиск:</label>
            <input type="text" id="searchInput" class="search-input" placeholder="Введите название номенклатуры...">
            <div class="stats">
                Показано: <span id="visibleCount">0</span> из <span id="totalCount">0</span> позиций
            </div>
        </div>
        
        <div class="table-container">
            {table}
        </div>
    </div>

    <script>
        function filterTable() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const table = document.querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {{
                    row.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    row.classList.add('hidden');
                }}
            }});
            
            document.getElementById('visibleCount').textContent = visibleCount;
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            const totalRows = document.querySelectorAll('tbody tr').length;
            document.getElementById('totalCount').textContent = totalRows;
            document.getElementById('visibleCount').textContent = totalRows;
            
            document.getElementById('searchInput').addEventListener('input', filterTable);
        }});
    </script>
</body>
</html>
'''
    
    html_table = df_with_numbers.to_html(index=False, border=0, classes='dataframe', justify='left', escape=False)
    
    html_result = html_template.format(table=html_table)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_result)


def save_failures_to_html(group_data, failed_items, output_file):
    """Сохраняет отчет о необработанных позициях в HTML с возможностью сортировки."""
    html_template = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчет о необработанных позициях</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 1400px; margin: 20px auto; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h2 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            font-size: 14px; 
            margin-top: 20px;
        }}
        thead th {{
            background: #d9534f;
            color: white;
            padding: 12px 8px;
            text-align: left;
            cursor: pointer;
            position: relative;
        }}
        thead th::after {{
            content: ' ↕';
            opacity: 0.5;
        }}
        thead th.sort-asc::after {{
            content: ' ↑';
            opacity: 1;
        }}
        thead th.sort-desc::after {{
            content: ' ↓';
            opacity: 1;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Пропущенные группы товаров</h2>
        <table id="skipped-table">
            <thead><tr><th style="width: 50px;">№</th><th>Название группы</th></tr></thead>
            <tbody>
                {skipped_rows}
            </tbody>
        </table>

        <h2 style="margin-top: 30px;">Товары с ошибками расчета</h2>
        <table id="failed-table">
            <thead><tr><th style="width: 50px;" data-sort-type="number">№</th><th data-sort-type="string">Номенклатура</th><th data-sort-type="string">Причина сбоя</th><th data-sort-type="number">Отклонение (кг)</th></tr></thead>
            <tbody>
                {failed_rows}
            </tbody>
        </table>
    </div>

<script>
function sortTable(table, column, asc = true) {{
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    const headerCell = table.querySelector(`thead th:nth-child(${{column + 1}})`);
    const sortType = headerCell.dataset.sortType || 'string';

    const sortedRows = rows.sort((a, b) => {{
        let aColText = a.querySelector(`td:nth-child(${{column + 1}})`).textContent.trim();
        let bColText = b.querySelector(`td:nth-child(${{column + 1}})`).textContent.trim();

        if (sortType === 'number') {{
            aColText = parseFloat(aColText.replace(',', '.')) || 0;
            bColText = parseFloat(bColText.replace(',', '.')) || 0;
        }} else {{
            aColText = aColText.toLowerCase();
            bColText = bColText.toLowerCase();
        }}

        return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    }});

    while (tBody.firstChild) {{
        tBody.removeChild(tBody.firstChild);
    }}

    tBody.append(...sortedRows);

    table.querySelectorAll("thead th").forEach(th => th.classList.remove("sort-asc", "sort-desc"));
    headerCell.classList.toggle("sort-asc", asc);
    headerCell.classList.toggle("sort-desc", !asc);
}}

document.querySelectorAll("#failed-table thead th").forEach(headerCell => {{
    headerCell.addEventListener("click", () => {{
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAsc = headerCell.classList.contains("sort-asc");

        sortTable(tableElement, headerIndex, !currentIsAsc);
    }});
}});
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

    final_html = html_template.format(skipped_rows=skipped_html, failed_rows=failed_html)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)


def main():
    """
    Основная функция для расчета коэффициентов с улучшенной обработкой ошибок.
    
    Логирует прогресс и ошибки в файлы журналов.
    """
    try:
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
        print(f"Начинаю улучшенный анализ данных...\\nИсходный файл: {csv_file}")
        
        nomenclature_data, group_data = parse_inventory_data_improved(csv_file)
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
                    results.append(coefficients)
                    print(f"Обработано {i}/{len(nomenclature_data)}: {nomenclature['name']}")
                    print(f"  Коэффициенты: a={coefficients['a']}, b={coefficients['b']}, точность={coefficients['accuracy']}%")
                else:
                    print(f"Ошибка обработки {i}/{len(nomenclature_data)}: {nomenclature['name']}")
                    print(f"  Причина: {reason}")
                    # Проверяем, что эта номенклатура еще не была успешно обработана
                    already_processed = any(item['nomenclature'] == nomenclature['name'] for item in results)
                    if not already_processed:
                        failed_items.append({'name': nomenclature['name'], 'reason': reason, 'weight': weight})
        
        if results:
            df_results = pd.DataFrame(results)
            df_results['Дата_расчета'] = datetime.now().strftime('%d.%m.%y')
            df_results['Примечание'] = df_results.apply(
                lambda row: f"Расчет по данным за период {row['period']}. Усушка {row['shrinkage']:.3f} кг за 7 дней хранения.",
                axis=1
            )
            
            df_results = df_results.rename(columns={
                'nomenclature': 'Номенклатура',
                'a': 'a',
                'b': 'b (день⁻¹)',
                'c': 'c',
                'accuracy': 'Точность (%)',
                'Дата_расчета': 'Дата_расчета',
                'Примечание': 'Примечание'
            })
            
            df_results = df_results[['Номенклатура', 'a', 'b (день⁻¹)', 'c', 'Точность (%)', 'Дата_расчета', 'Примечание']]
            
            os.makedirs(os.path.dirname(csv_output_file), exist_ok=True)
            
            df_results.to_csv(csv_output_file, index=False, encoding='utf-8')
            print(f"\\nРезультаты сохранены в CSV: {csv_output_file}")
            
            save_to_html(df_results, html_output_file)
            print(f"Результаты сохранены в HTML: {html_output_file}")
            
            print(f"Рассчитано коэффициентов: {len(results)}")
        
            print("\\nРезультаты:")
            for _, row in df_results.iterrows():
                print(f"{row['Номенклатура']}: a={row['a']}, b={row['b (день⁻¹)']}, точность={row['Точность (%)']}% ")
        
        else:
            print("Не удалось рассчитать коэффициенты для ни одной номенклатуры")

        # Финальная проверка failed_items: удаляем из него позиции, которые есть в результатах
        if results and failed_items:
            successful_names = {item['nomenclature'] for item in results}
            failed_items = [item for item in failed_items if item['name'] not in successful_names]
            # Также удаляем дубликаты из failed_items
            seen_failed_names = set()
            unique_failed_items = []
            for item in failed_items:
                if item['name'] not in seen_failed_names:
                    unique_failed_items.append(item)
                    seen_failed_names.add(item['name'])
            failed_items = unique_failed_items

        if group_data or failed_items:
            save_failures_to_html(group_data, failed_items, html_failures_output_file)
            print(f"Отчет по необработанным позициям сохранен в: {html_failures_output_file}")

    except Exception as e:
        error_logger.error(f"Критическая ошибка в main(): {str(e)}", exc_info=True)
        print(f"Произошла ошибка: {str(e)}. Подробности в логе ошибок.")
        raise  # Пробрасываем исключение дальше для GUI
    finally:
        info_logger.info("Завершение работы скрипта")


def load_config() -> None:
    """Загружает конфигурацию из файла JSON в корне проекта."""
    global CONFIG
    try:
        # Абсолютный путь к текущему скрипту
        script_path = os.path.abspath(__file__)
        # Абсолютный путь к папке скриптов
        script_dir = os.path.dirname(script_path)
        # Абсолютный путь к корневой папке проекта (на уровень выше)
        project_root = os.path.dirname(script_dir)
        # Путь к файлу конфигурации
        config_path = os.path.join(project_root, 'config.json')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                CONFIG.update(json.load(f))
    except Exception as e:
        logging.error(f"Ошибка загрузки конфигурации: {str(e)}")


if __name__ == "__main__":
    load_config()
    main()