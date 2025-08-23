import pandas as pd
import os
import re
from typing import Dict, Tuple

def extract_shrinkage_from_note(note: str) -> float:
    """
    Извлекает значение усушки из примечания.
    
    Args:
        note: Строка примечания
        
    Returns:
        Значение усушки в кг или 0, если не удалось извлечь
    """
    if not isinstance(note, str):
        return 0.0
        
    # Ищем шаблон "Усушка X.XXX кг"
    match = re.search(r'Усушка\s+(\d+(?:[.,]\d+)?)\s*кг', note.replace(',', '.'))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0

def load_actual_shrinkage(coefficients_file: str) -> Dict[str, float]:
    """
    Загружает фактические значения усушки из файла с коэффициентами.
    
    Args:
        coefficients_file: Путь к CSV файлу с коэффициентами
        
    Returns:
        Словарь с номенклатурами и их фактической усушкой
    """
    if not os.path.exists(coefficients_file):
        raise FileNotFoundError(f"Файл с коэффициентами {coefficients_file} не найден")
    
    df = pd.read_csv(coefficients_file)
    actual_shrinkage = {}
    
    for _, row in df.iterrows():
        nomenclature = row['Номенклатура']
        note = row['Примечание']
        shrinkage = extract_shrinkage_from_note(note)
        actual_shrinkage[nomenclature] = shrinkage
    
    return actual_shrinkage

def load_predicted_shrinkage(prelim_file: str) -> Dict[str, float]:
    """
    Загружает предсказанные значения усушки из файла предварительного расчета.
    
    Args:
        prelim_file: Путь к CSV файлу с предварительным расчетом
        
    Returns:
        Словарь с номенклатурами и их предсказанной усушкой
    """
    if not os.path.exists(prelim_file):
        raise FileNotFoundError(f"Файл с предварительным расчетом {prelim_file} не найден")
    
    df = pd.read_csv(prelim_file)
    predicted_shrinkage = {}
    
    for _, row in df.iterrows():
        nomenclature = row['Номенклатура']
        shrinkage = row['Прогнозируемая_усушка_кг']
        predicted_shrinkage[nomenclature] = shrinkage
    
    return predicted_shrinkage

def compare_shrinkage(actual: Dict[str, float], predicted: Dict[str, float]) -> pd.DataFrame:
    """
    Сравнивает фактические и предсказанные значения усушки.
    
    Args:
        actual: Словарь с фактической усушкой
        predicted: Словарь с предсказанной усушкой
        
    Returns:
        DataFrame с результатами сравнения
    """
    comparison_data = []
    
    # Для каждой номенклатуры, которая есть в обоих словарях
    all_nomenclatures = set(actual.keys()) | set(predicted.keys())
    
    for nomenclature in all_nomenclatures:
        actual_value = actual.get(nomenclature, 0.0)
        predicted_value = predicted.get(nomenclature, 0.0)
        
        # Рассчитываем отклонение
        difference = predicted_value - actual_value
        # Рассчитываем процентное отклонение (от фактического значения)
        if actual_value > 0:
            percent_diff = (difference / actual_value) * 100
        else:
            percent_diff = 0 if difference == 0 else float('inf')
            
        comparison_data.append({
            'Номенклатура': nomenclature,
            'Фактическая_усушка_кг': actual_value,
            'Предсказанная_усушка_кг': predicted_value,
            'Отклонение_кг': difference,
            'Процент_отклонения_%': percent_diff
        })
    
    # Создаем DataFrame и сортируем по абсолютному значению отклонения
    df = pd.DataFrame(comparison_data)
    df['Абсолютное_отклонение'] = df['Отклонение_кг'].abs()
    df = df.sort_values('Абсолютное_отклонение', ascending=False).drop('Абсолютное_отклонение', axis=1)
    
    return df

def main():
    """
    Основная функция для сравнения усушки.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Пути к файлам
        coefficients_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
        prelim_file = os.path.join(project_root, "результаты", "предварительный_расчет_усушки.csv")
        output_file = os.path.join(project_root, "результаты", "сравнение_усушки.csv")
        html_output_file = os.path.join(project_root, "результаты", "сравнение_усушки.html")
        
        print("Загрузка фактических данных об усушке...")
        actual_shrinkage = load_actual_shrinkage(coefficients_file)
        print(f"Загружены данные по {len(actual_shrinkage)} номенклатурам")
        
        print("Загрузка предсказанных данных об усушке...")
        predicted_shrinkage = load_predicted_shrinkage(prelim_file)
        print(f"Загружены данные по {len(predicted_shrinkage)} номенклатурам")
        
        print("Сравнение усушки...")
        comparison_df = compare_shrinkage(actual_shrinkage, predicted_shrinkage)
        
        if not comparison_df.empty:
            # Сохраняем результаты
            comparison_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Результаты сравнения сохранены в файл: {output_file}")
            
            # Создаем HTML отчет
            html_template = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Сравнение фактической и предсказанной усушки</title>
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
        <h2>Сравнение фактической и предсказанной усушки</h2>
        {table}
    </div>
</body>
</html>
'''
            
            # Форматируем данные для HTML, добавляя цветовую индикацию
            styled_df = comparison_df.copy()
            styled_df['Процент_отклонения_%'] = styled_df['Процент_отклонения_%'].apply(
                lambda x: f'<span class="positive">+{x:.2f}</span>' if x > 0 else (
                    f'<span class="negative">{x:.2f}</span>' if x < 0 else f'<span class="zero">{x:.2f}</span>'
                )
            )
            
            html_table = styled_df.to_html(index=False, border=0, classes='dataframe', justify='left', escape=False)
            html_result = html_template.format(table=html_table)
            
            with open(html_output_file, 'w', encoding='utf-8') as f:
                f.write(html_result)
            print(f"HTML отчет сохранен в файл: {html_output_file}")
            
            # Выводим сводную статистику
            total_actual = comparison_df['Фактическая_усушка_кг'].sum()
            total_predicted = comparison_df['Предсказанная_усушка_кг'].sum()
            avg_deviation = (total_predicted - total_actual) / len(comparison_df) if len(comparison_df) > 0 else 0
            avg_percent_deviation = comparison_df['Процент_отклонения_%'].mean()
            
            print("\nСводная статистика:")
            print(f"Общая фактическая усушка: {total_actual:.3f} кг")
            print(f"Общая предсказанная усушка: {total_predicted:.3f} кг")
            print(f"Среднее отклонение: {avg_deviation:.3f} кг")
            print(f"Среднее процентное отклонение: {avg_percent_deviation:.2f}%")
            
            # Выводим несколько примеров с наибольшими отклонениями
            print("\nТоп-10 номенклатур с наибольшими отклонениями:")
            for i, (_, row) in enumerate(comparison_df.head(10).iterrows(), 1):
                print(f"{i}. {row['Номенклатура']}: "
                      f"факт={row['Фактическая_усушка_кг']:.3f} кг, "
                      f"прогноз={row['Предсказанная_усушка_кг']:.3f} кг, "
                      f"отклонение={row['Отклонение_кг']:.3f} кг "
                      f"({row['Процент_отклонения_%']:.2f}%)")
        else:
            print("Нет данных для сравнения")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()