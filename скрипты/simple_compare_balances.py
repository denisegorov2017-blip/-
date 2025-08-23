import pandas as pd
import os

def load_coefficients_data(coefficients_file):
    """Загружает данные из файла с коэффициентами."""
    if not os.path.exists(coefficients_file):
        raise FileNotFoundError(f"Файл с коэффициентами {coefficients_file} не найден")
    return pd.read_csv(coefficients_file)

def extract_initial_balance_from_main_report(csv_file, nomenclature):
    """Извлекает начальный остаток для номенклатуры из основного отчета."""
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
            row_str == nomenclature
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

def extract_initial_balance_from_prelim_report(csv_file, nomenclature):
    """Извлекает начальный остаток для номенклатуры из предварительного отчета."""
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
            row_str == nomenclature
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

def compare_initial_balances():
    """Сравнивает начальные остатки из разных источников."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Пути к файлам
        coefficients_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
        main_report_file = os.path.join(project_root, "исходные_данные", "Для_расчета_коэфф", "sheet_1_Лист_1.csv")
        prelim_report_file = os.path.join(project_root, "исходные_данные", "Для_передварительной_усушки", "sheet_1_Лист_1_prelim.csv")
        
        print("Загрузка данных о коэффициентах...")
        coefficients_df = load_coefficients_data(coefficients_file)
        print(f"Загружены данные по {len(coefficients_df)} номенклатурам")
        
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
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df['Абсолютная_разница'] = comparison_df['Разница_кг'].abs()
        comparison_df = comparison_df.sort_values('Абсолютная_разница', ascending=False).drop('Абсолютная_разница', axis=1)
        
        # Выводим результаты
        print("\nСводная статистика:")
        total_main = comparison_df['Остаток_основной_отчет_кг'].sum()
        total_prelim = comparison_df['Остаток_предварительный_отчет_кг'].sum()
        print(f"Общий остаток в основном отчете: {total_main:.3f} кг")
        print(f"Общий остаток в предварительном отчете: {total_prelim:.3f} кг")
        print(f"Разница в общих остатках: {total_prelim - total_main:.3f} кг")
        
        # Выводим несколько примеров с наибольшими разницами
        print("\nТоп-10 номенклатур с наибольшими разницами в остатках:")
        for i, (_, row) in enumerate(comparison_df.head(10).iterrows(), 1):
            if abs(row['Разница_кг']) > 0.001:  # Выводим только значимые различия
                print(f"{i}. {row['Номенклатура']}: "
                      f"основной={row['Остаток_основной_отчет_кг']:.3f} кг, "
                      f"предварительный={row['Остаток_предварительный_отчет_кг']:.3f} кг, "
                      f"разница={row['Разница_кг']:.3f} кг")
        
        # Сохраняем результаты в CSV
        output_file = os.path.join(project_root, "результаты", "сравнение_остатков.csv")
        comparison_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nРезультаты сохранены в файл: {output_file}")
                          
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    compare_initial_balances()