import pandas as pd
import os
import re
from typing import Dict, Tuple

def extract_initial_balance_from_main_report(csv_file: str, nomenclature: str) -> float:
    \"\"\"
    Извлекает начальный остаток для номенклатуры из основного отчета.
    
    Args:
        csv_file: Путь к CSV файлу с отчетом
        nomenclature: Название номенклатуры
        
    Returns:
        Начальный остаток в кг или 0, если не найден
    \"\"\"
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Файл отчета {csv_file} не найден")
        
    # Читаем CSV файл
    df = pd.read_csv(csv_file, header=None, dtype=str, on_bad_lines='skip')
    
    # Ищем строку с номенклатурой
    for idx, row in df.iterrows():
        if pd.isna(row[0]) or not str(row[0]).strip():
            continue
            
        row_str = str(row[0]).strip()
        # Проверяем, является ли строка номенклатурой 
        is_nomenclature = (
            idx > 5 and 
            pd.notna(row[1]) and str(row[1]).strip() and 
            row_str == nomenclature and
            not any(keyword in row_str for keyword in [
                'Отчет отдела', 'Приходная накладная', 'Инвентаризация', 
                'Списание', 'Перемещение', 'Пересортица', 'Склад', 
                'Номенклатура', 'Документ движения', 'Партия.Дата прихода', 'Итого'
            ])
        )
        
        if is_nomenclature:
            try:
                # Очистка и преобразование остатка
                initial_balance_str = str(row[1]).strip().replace(',', '.')
                initial_balance = float(initial_balance_str)
                return initial_balance
            except (ValueError, IndexError):
                return 0.0
                    
    return 0.0

def extract_initial_balance_from_prelim_report(csv_file: str, nomenclature: str) -> float:
    \"\"\"
    Извлекает начальный остаток для номенклатуры из предварительного отчета.
    В предварительном отчете мы суммируем остатки по всем партиям.
    
    Args:
        csv_file: Путь к CSV файлу с отчетом
        nomenclature: Название номенклатуры
        
    Returns:
        Начальный остаток в кг или 0, если не найден
    \"\"\"
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Файл отчета {csv_file} не найден")
        
    # Читаем CSV файл
    df = pd.read_csv(csv_file, header=None, dtype=str, on_bad_lines='skip')
    
    current_nomenclature = None
    total_balance = 0.0
    
    # Ищем строку с номенклатурой и суммируем партии
    for idx, row in df.iterrows():
        if pd.isna(row[0]) or not str(row[0]).strip():
            continue
            
        row_str = str(row[0]).strip()
        
        # Проверяем, является ли строка номенклатурой 
        is_nomenclature = (
            idx > 5 and 
            pd.notna(row[1]) and str(row[1]).strip() and 
            not any(keyword in row_str for keyword in [
                'Отчет отдела', 'Приходная накладная', 'Инвентаризация', 
                'Списание', 'Перемещение', 'Пересортица', 'Склад', 
                'Номенклатура', 'Документ движения', 'Партия.Дата прихода', 'Итого'
            ]) and
            # Проверяем, что это не дата партии
            not (re.match(r'\\d{2}\\.\\d{2}\\.\\d{4} \\d{1,2}:\\d{2}:\\d{2}', row_str) or 
                 re.match(r'\\d{2}\\.\\d{2}\\.\\d{4} \\d{1,2}:\\d{2}', row_str))
        )
        
        if is_nomenclature:
            # Если это та номенклатура, которую мы ищем, начинаем суммировать партии
            if row_str == nomenclature:
                current_nomenclature = row_str
                # Добавляем общий остаток номенклатуры
                try:
                    initial_balance_str = str(row[1]).strip().replace(',', '.')
                    initial_balance = float(initial_balance_str)
                    total_balance = initial_balance
                    # После нахождения номенклатуры мы не прекращаем обработку, 
                    # так как нужно найти все партии
                except (ValueError, IndexError):
                    pass
            else:
                # Если это другая номенклатура, и мы уже нашли нужную, 
                # то прекращаем обработку (для простоты)
                if current_nomenclature == nomenclature:
                    break
        # Если у нас есть текущая номенклатура и строка - это партия
        elif current_nomenclature == nomenclature and row_str:
            # Проверяем, является ли строка датой партии
            if (re.match(r'\\d{2}\\.\\d{2}\\.\\d{4} \\d{1,2}:\\d{2}:\\d{2}', row_str) or 
                re.match(r'\\d{2}\\.\\d{2}\\.\\d{4} \\d{1,2}:\\d{2}', row_str)):
                # Но в предварительном расчете мы используем сумму партий, 
                # которая уже есть как общий остаток номенклатуры
                # Поэтому мы не суммируем партии отдельно, а используем общий остаток
                pass
                    
    return total_balance

def load_coefficients_data(coefficients_file: str) -> pd.DataFrame:
    \"\"\"
    Загружает данные из файла с коэффициентами.
    
    Args:
        coefficients_file: Путь к CSV файлу с коэффициентами
        
    Returns:
        DataFrame с данными
    \"\"\"
    if not os.path.exists(coefficients_file):
        raise FileNotFoundError(f"Файл с коэффициентами {coefficients_file} не найден")
    
    return pd.read_csv(coefficients_file)

def load_prelim_data(prelim_file: str) -> pd.DataFrame:
    \"\"\"
    Загружает данные из файла предварительного расчета.
    
    Args:
        prelim_file: Путь к CSV файлу с предварительным расчетом
        
    Returns:
        DataFrame с данными
    \"\"\"
    if not os.path.exists(prelim_file):
        raise FileNotFoundError(f"Файл с предварительным расчетом {prelim_file} не найден")
    
    return pd.read_csv(prelim_file)

def compare_initial_balances(
    coefficients_df: pd.DataFrame, 
    main_report_file: str, 
    prelim_report_file: str
) -> pd.DataFrame:
    \"\"\"
    Сравнивает начальные остатки из разных источников.
    
    Args:
        coefficients_df: DataFrame с коэффициентами
        main_report_file: Путь к основному отчету
        prelim_report_file: Путь к предварительному отчету
        
    Returns:
        DataFrame с результатами сравнения
    \"\"\"
    comparison_data = []
    
    for _, row in coefficients_df.iterrows():
        nomenclature = row['Номенклатура']
        
        # Извлекаем начальный остаток из основного отчета
        main_balance = extract_initial_balance_from_main_report(main_report_file, nomenclature)
        
        # Извлекаем начальный остаток из предварительного отчета
        prelim_balance = extract_initial_balance_from_prelim_report(prelim_report_file, nomenclature)
        
        # Рассчитываем разницу
        difference = prelim_balance - main_balance
        
        comparison_data.append({
            'Номенклатура': nomenclature,
            'Остаток_основной_отчет_кг': main_balance,
            'Остаток_предварительный_отчет_кг': prelim_balance,
            'Разница_кг': difference
        })
    
    # Создаем DataFrame и сортируем по абсолютному значению разницы
    df = pd.DataFrame(comparison_data)
    df['Абсолютная_разница'] = df['Разница_кг'].abs()
    df = df.sort_values('Абсолютная_разница', ascending=False).drop('Абсолютная_разница', axis=1)
    
    return df

def main():
    \"\"\"
    Основная функция для сравнения начальных остатков.
    \"\"\"
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Пути к файлам
        coefficients_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
        main_report_file = os.path.join(project_root, "исходные_данные", "sheet_1_Лист_1.csv")
        prelim_report_file = os.path.join(project_root, "исходные_данные", "Для_передварительной_усушки", "sheet_1_Лист_1_prelim.csv")
        output_file = os.path.join(project_root, "результаты", "сравнение_остатков.csv")
        html_output_file = os.path.join(project_root, "результаты", "сравнение_остатков.html")
        
        print("Загрузка данных о коэффициентах...")
        coefficients_df = load_coefficients_data(coefficients_file)
        print(f"Загружены данные по {len(coefficients_df)} номенклатурам")
        
        print("Сравнение начальных остатков...")
        comparison_df = compare_initial_balances(coefficients_df, main_report_file, prelim_report_file)
        
        if not comparison_df.empty:
            # Сохраняем результаты
            comparison_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Результаты сравнения остатков сохранены в файл: {output_file}")
            
            # Создаем HTML отчет
            html_template = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Сравнение начальных остатков</title>
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
        .positive {{ color: red; }}
        .negative {{ color: green; }}
        .zero {{ color: black; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Сравнение начальных остатков</h2>
        {table}
    </div>
</body>
</html>
'''
            
            # Форматируем данные для HTML
            html_table = comparison_df.to_html(index=False, border=0, classes='dataframe', justify='left', escape=False)
            html_result = html_template.format(table=html_table)
            
            with open(html_output_file, 'w', encoding='utf-8') as f:
                f.write(html_result)
            print(f"HTML отчет сохранен в файл: {html_output_file}")
            
            # Выводим сводную статистику
            total_main = comparison_df['Остаток_основной_отчет_кг'].sum()
            total_prelim = comparison_df['Остаток_предварительный_отчет_кг'].sum()
            
            print("\\nСводная статистика:")
            print(f"Общий остаток в основном отчете: {total_main:.3f} кг")
            print(f"Общий остаток в предварительном отчете: {total_prelim:.3f} кг")
            print(f"Разница в общих остатках: {total_prelim - total_main:.3f} кг")
            
            # Выводим несколько примеров с наибольшими разницами
            print("\\nТоп-10 номенклатур с наибольшими разницами в остатках:")
            for i, (_, row) in enumerate(comparison_df.head(10).iterrows(), 1):
                if abs(row['Разница_кг']) > 0.001:  # Выводим только значимые различия
                    print(f"{i}. {row['Номенклатура']}: "
                          f"основной={row['Остаток_основной_отчет_кг']:.3f} кг, "
                          f"предварительный={row['Остаток_предварительный_отчет_кг']:.3f} кг, "
                          f"разница={row['Разница_кг']:.3f} кг")
                          
        else:
            print("Нет данных для сравнения")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()