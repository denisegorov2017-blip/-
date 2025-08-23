import pandas as pd
import numpy as np
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List
from analytics import forecast_shrinkage

def load_coefficients(coefficients_file: str) -> Dict[str, Dict[str, float]]:
    """
    Загружает коэффициенты усушки из CSV файла в словарь.
    
    Args:
        coefficients_file: Путь к CSV файлу с коэффициентами
        
    Returns:
        Словарь, где ключ - название номенклатуры, значение - словарь коэффициентов
    """
    if not os.path.exists(coefficients_file):
        raise FileNotFoundError(f"Файл с коэффициентами {coefficients_file} не найден")
    
    df = pd.read_csv(coefficients_file)
    coefficients = {}
    
    for _, row in df.iterrows():
        coefficients[row['Номенклатура']] = {
            'a': row['a'],
            'b': row['b (день⁻¹)'],
            'c': row['c']
        }
    
    return coefficients

def parse_inventory_for_preliminary(csv_file: str, target_balance_date: datetime = None) -> Dict[str, float]:
    """
    Парсит CSV файл с отчетом о товародвижении для извлечения начальных остатков.
    Может извлекать остатки на заданную дату, если указана target_balance_date.
    
    Args:
        csv_file: Путь к CSV файлу с отчетом
        target_balance_date: Дата, на которую нужно извлечь начальные остатки
        
    Returns:
        Словарь, где ключ - название номенклатуры, значение - начальный остаток в кг
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Файл с отчетом {csv_file} не найден")
        
    # Читаем CSV файл
    df = pd.read_csv(csv_file, header=None, dtype=str, on_bad_lines='skip')
    inventory_data = {}
    
    current_nomenclature = None
    current_batches = {}
    
    # Переменные для отслеживания текущей даты остатков
    current_balance_date = None  # Дата, на которую рассчитаны остатки в текущей секции
    collecting_balances_for_target_date = False  # Флаг сбора остатков для target_balance_date
    
    # Хранилище данных для target_balance_date
    balances_for_target_date = {}  # {название_номенклатуры: остаток}
    
    def save_current_nomenclature(is_collecting_default=False, is_collecting_target=False):
        """Сохраняет данные по текущей номенклатуре"""
        nonlocal current_nomenclature, current_batches, inventory_data, balances_for_target_date
        if current_nomenclature and current_batches:
            # Рассчитываем суммарный остаток по всем партиям
            total_balance = sum(current_batches.values())
            
            # Сохраняем для парсинга по умолчанию
            if is_collecting_default:
                inventory_data[current_nomenclature] = total_balance
            
            # Сохраняем для target_balance_date
            if is_collecting_target:
                balances_for_target_date[current_nomenclature] = total_balance
                
            current_batches.clear()

    # Пропускаем заголовки и ищем строки с номенклатурами и остатками
    for idx, row in df.iterrows():
        # Проверяем, что строка не пустая
        if pd.isna(row[0]) or not str(row[0]).strip():
            continue
            
        row_str = str(row[0]).strip()
        
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
        
        # Проверяем, является ли строка номенклатурой 
        # (наличие данных в колонке остатка и отсутствие ключевых слов)
        is_nomenclature = (
            idx > 5 and 
            pd.notna(row[1]) and str(row[1]).strip() and 
            not any(keyword in row_str for keyword in [
                'Отчет отдела', 'Приходная накладная', 'Инвентаризация', 
                'Списание', 'Перемещение', 'Пересортица', 'Склад', 
                'Номенклатура', 'Документ движения', 'Партия.Дата прихода', 'Итого'
            ]) and
            # Проверяем, что это не дата партии
            not (re.match(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}:\d{2}', row_str) or 
                 re.match(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}', row_str))
        )
        
        if is_nomenclature:
            # Сохраняем предыдущую номенклатуру
            save_current_nomenclature(
                is_collecting_default=collecting_by_default,
                is_collecting_target=collecting_balances_for_target_date
            )
            
            # Начинаем новую номенклатуру
            current_nomenclature = row_str
            current_batches = {}
            
            # Проверяем, есть ли остаток у номенклатуры
            try:
                # Очистка и преобразование остатка
                initial_balance_str = str(row[1]).strip().replace(',', '.')
                initial_balance = float(initial_balance_str)
                
                # Проверка, что это действительно число (не заголовок)
                if current_nomenclature and initial_balance >= 0:
                    # Инициализируем словарь для партий этой номенклатуры
                    # Для простоты считаем весь остаток одной партией
                    # В реальном сценарии здесь нужно было бы извлекать партии
                    current_batches["общий_остаток"] = initial_balance
            except (ValueError, IndexError):
                # Если не удалось преобразовать в число, пропускаем эту строку
                current_nomenclature = None
                continue
        elif current_nomenclature and row_str:
            # Если у нас есть текущая номенклатура, ищем партии
            # Проверяем, является ли строка датой партии (формат дд.мм.гггг чч:мм:сс или дд.мм.гггг чч:мм)
            if (re.match(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}:\d{2}', row_str) or
                re.match(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}', row_str)):
                
                try:
                    # Проверяем, есть ли остаток в колонке B
                    if pd.notna(row[1]) and str(row[1]).strip():
                        # Очистка и преобразование остатка
                        balance_str = str(row[1]).strip().replace(',', '.')
                        balance = float(balance_str)
                        
                        # Проверка, что это действительно число и остаток положительный
                        if balance >= 0:
                            # Сохраняем партию и остаток
                            current_batches[row_str] = balance
                except (ValueError, IndexError):
                    # Если не удалось преобразовать в число, пропускаем эту строку
                    continue

    # Сохраняем последнюю номенклатуру
    save_current_nomenclature(
        is_collecting_default=collecting_by_default,
        is_collecting_target=collecting_balances_for_target_date
    )
    
    # Возвращаем результаты в зависимости от режима
    if target_balance_date:
        # Возвращаем данные, собранные для target_balance_date
        print(f"Возвращаем данные для остатков на {target_balance_date.strftime('%d.%m.%Y')}")
        return balances_for_target_date
    else:
        # Возвращаем данные, собранные по умолчанию
        print("Возвращаем данные по умолчанию")
        return inventory_data

def calculate_preliminary_shrinkage(
    coefficients: Dict[str, Dict[str, float]], 
    initial_balances: Dict[str, float],
    days: int = 7
) -> List[Dict]:
    """
    Рассчитывает предварительную усушку для всех номенклатур с учетом партий.
    
    Args:
        coefficients: Словарь с коэффициентами для каждой номенклатуры
        initial_balances: Словарь с остатками по партиям для каждой номенклатуры
        days: Количество дней для прогноза (по умолчанию 7)
        
    Returns:
        Список словарей с результатами расчета
    """
    results = []
    
    # Проходим по всем номенклатурам с остатками
    for nomenclature, initial_mass in initial_balances.items():
        if nomenclature in coefficients:
            coef = coefficients[nomenclature]
            # Рассчитываем усушку для этой номенклатуры
            forecast = forecast_shrinkage(coef, initial_mass, days)
            
            # Добавляем результат для номенклатуры
            results.append({
                'Номенклатура': nomenclature,
                'Начальный_остаток_кг': initial_mass,
                'Прогнозируемая_усушка_кг': forecast['total_shrinkage'],
                'Конечный_остаток_кг': forecast['final_mass'],
                'a': coef['a'],
                'b': coef['b'],
                'c': coef['c']
            })
        else:
            print(f"Коэффициенты для номенклатуры '{nomenclature}' не найдены")
    
    return results

def save_results_to_csv(results: List[Dict], output_file: str):
    """
    Сохраняет результаты в CSV файл.
    
    Args:
        results: Список словарей с результатами
        output_file: Путь к выходному файлу
    """
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Результаты сохранены в файл: {output_file}")

def save_results_to_html(results: List[Dict], output_file: str):
    """
    Сохраняет результаты в HTML файл.
    
    Args:
        results: Список словарей с результатами
        output_file: Путь к выходному файлу
    """
    df = pd.DataFrame(results)
    
    html_template = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Предварительный расчет усушки</title>
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
            background: #4CAF50;
            color: white;
            padding: 12px 8px;
            text-align: left;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #e8f5e8; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Предварительный расчет усушки</h2>
        {table}
    </div>
</body>
</html>
'''
    
    html_table = df.to_html(index=False, border=0, classes='dataframe', justify='left', escape=False)
    html_result = html_template.format(table=html_table)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_result)
    print(f"Результаты сохранены в файл: {output_file}")

def main():
    """
    Основная функция для предварительного расчета усушки.
    """
    try:
        import argparse
        
        parser = argparse.ArgumentParser(description="Предварительный расчет усушки")
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
        
        # Пути к файлам
        coefficients_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
        # ПРЕДПОЛОЖЕНИЕ: CSV файл с исходными данными для предварительного расчета 
        # должен быть создан из PDF "14,07,25- 21.07.25 Для предварительного расчета усушки.pdf"
        # Например, сохраним его как "sheet_1_Лист_1_prelim.csv" в папке исходные_данные\Для_передварительной_усушки
        csv_file = os.path.join(project_root, "исходные_данные", "Для_передварительной_усушки", "sheet_1_Лист_1_prelim.csv")
        csv_output_file = os.path.join(project_root, "результаты", "предварительный_расчет_усушки.csv")
        html_output_file = os.path.join(project_root, "результаты", "предварительный_расчет_усушки.html")
        
        print("Загрузка коэффициентов...")
        coefficients = load_coefficients(coefficients_file)
        print(f"Загружено коэффициентов для {len(coefficients)} номенклатур")
        
        print("Парсинг исходных данных...")
        initial_balances = parse_inventory_for_preliminary(csv_file, target_balance_date)
        print(f"Найдены начальные остатки для {len(initial_balances)} номенклатур")
        
        print("Расчет предварительной усушки...")
        results = calculate_preliminary_shrinkage(coefficients, initial_balances)
        print(f"Рассчитана предварительная усушка для {len(results)} номенклатур")
        
        if results:
            save_results_to_csv(results, csv_output_file)
            save_results_to_html(results, html_output_file)
            print("\nРезультаты расчета:")
            df_results = pd.DataFrame(results)
            for _, row in df_results.iterrows():
                print(f"{row['Номенклатура']}: Начальный остаток={row['Начальный_остаток_кг']:.3f} кг, "
                      f"Прогнозируемая усушка={row['Прогнозируемая_усушка_кг']:.3f} кг, "
                      f"Конечный остаток={row['Конечный_остаток_кг']:.3f} кг")
        else:
            print("Не удалось рассчитать предварительную усушку ни для одной номенклатуры")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()