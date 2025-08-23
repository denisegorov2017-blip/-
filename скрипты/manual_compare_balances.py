import pandas as pd
import os

# Функция для парсинга файла с отчетом
def parse_inventory_file(csv_file):
    # Проверка существования файла
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Файл отчета {csv_file} не найден")
        
    # Читаем CSV файл
    df = pd.read_csv(csv_file, header=None, dtype=str, on_bad_lines='skip')
    balances = {}
    
    # Ищем строки с номенклатурами и извлекаем остатки
    for idx, row in df.iterrows():
        # Пропускаем пустые строки
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
            ])
        )
        
        if is_nomenclature:
            try:
                # Очистка и преобразование остатка
                balance_str = str(row[1]).strip().replace(',', '.')
                balance = float(balance_str)
                balances[row_str] = balance
            except (ValueError, IndexError):
                # Если не удалось преобразовать в число, пропускаем
                continue
                    
    return balances

# Функция для сравнения остатков
def compare_balances(balances1, balances2, file1_name, file2_name):
    comparison_data = []
    
    # Собираем все номенклатуры
    all_nomenclatures = set(balances1.keys()) | set(balances2.keys())
    
    for nomenclature in all_nomenclatures:
        balance1 = balances1.get(nomenclature, 0.0)
        balance2 = balances2.get(nomenclature, 0.0)
        
        # Рассчитываем разницу
        difference = balance2 - balance1
        
        comparison_data.append({
            'Номенклатура': nomenclature,
            f'Остаток_{file1_name}_кг': balance1,
            f'Остаток_{file2_name}_кг': balance2,
            'Разница_кг': difference
        })
    
    # Создаем DataFrame и сортируем по абсолютному значению разницы
    df = pd.DataFrame(comparison_data)
    df['Абсолютная_разница'] = df['Разница_кг'].abs()
    df = df.sort_values('Абсолютная_разница', ascending=False).drop('Абсолютная_разница', axis=1)
    
    return df

# Основная функция
def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Пути к файлам
        main_report_file = os.path.join(project_root, "исходные_данные", "Для_расчета_коэфф", "sheet_1_Лист_1.csv")
        prelim_report_file = os.path.join(project_root, "исходные_данные", "Для_передварительной_усушки", "sheet_1_Лист_1_prelim.csv")
        
        print("Парсинг основного отчета...")
        main_balances = parse_inventory_file(main_report_file)
        print(f"Извлечены остатки по {len(main_balances)} номенклатурам из основного отчета")
        
        print("Парсинг предварительного отчета...")
        prelim_balances = parse_inventory_file(prelim_report_file)
        print(f"Извлечены остатки по {len(prelim_balances)} номенклатурам из предварительного отчета")
        
        print("Сравнение остатков...")
        comparison_df = compare_balances(main_balances, prelim_balances, "основной_отчет", "предварительный_отчет")
        
        if not comparison_df.empty:
            # Выводим сводную статистику
            total_main = comparison_df['Остаток_основной_отчет_кг'].sum()
            total_prelim = comparison_df['Остаток_предварительный_отчет_кг'].sum()
            
            print("\nСводная статистика:")
            print(f"Общий остаток в основном отчете: {total_main:.3f} кг")
            print(f"Общий остаток в предварительном отчете: {total_prelim:.3f} кг")
            print(f"Разница в общих остатках: {total_prelim - total_main:.3f} кг")
            
            # Выводим несколько примеров с наибольшими разницами
            print("\nТоп-20 номенклатур с наибольшими разницами в остатках:")
            count = 0
            for i, (_, row) in enumerate(comparison_df.iterrows(), 1):
                if abs(row['Разница_кг']) > 0.001:  # Выводим только значимые различия
                    print(f"{i}. {row['Номенклатура']}: "
                          f"основной={row['Остаток_основной_отчет_кг']:.3f} кг, "
                          f"предварительный={row['Остаток_предварительный_отчет_кг']:.3f} кг, "
                          f"разница={row['Разница_кг']:.3f} кг")
                    count += 1
                    if count >= 20:
                        break
            
            # Проверим, есть ли номенклатуры, у которых остатки совпадают
            matching_balances = comparison_df[abs(comparison_df['Разница_кг']) < 0.001]
            if not matching_balances.empty:
                print(f"\nНайдено {len(matching_balances)} номенклатур с совпадающими остатками (разница < 0.001 кг)")
            else:
                print("\nНе найдено номенклатур с совпадающими остатками")
                
            # Сохраняем результаты в CSV
            output_file = os.path.join(project_root, "результаты", "детальное_сравнение_остатков.csv")
            comparison_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\nРезультаты сохранены в файл: {output_file}")
                          
        else:
            print("Нет данных для сравнения")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()