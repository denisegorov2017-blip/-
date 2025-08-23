import pandas as pd
import os

def detailed_balance_comparison():
    """
    Детальное сравнение начальных остатков из двух отчетов.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Пути к файлам с результатами сравнения
        comparison_file = os.path.join(project_root, "результаты", "детальное_сравнение_остатков_v2.csv")
        
        if not os.path.exists(comparison_file):
            print(f"Файл сравнения {comparison_file} не найден")
            return
            
        # Читаем CSV файл с результатами сравнения
        df = pd.read_csv(comparison_file)
        
        print("Анализ результатов сравнения остатков...")
        print(f"Всего номенклатур в сравнении: {len(df)}")
        
        # Статистика по разницам
        df['Разница_абсолютная'] = abs(df['Разница_кг'])
        total_main = df['Остаток_основной_отчет_кг'].sum()
        total_prelim = df['Остаток_предварительный_отчет_кг'].sum()
        total_difference = total_prelim - total_main
        
        print(f"\nСводная статистика:")
        print(f"Общий остаток в основном отчете: {total_main:.3f} кг")
        print(f"Общий остаток в предварительном отчете: {total_prelim:.3f} кг")
        print(f"Разница в общих остатках: {total_difference:.3f} кг")
        
        # Находим позиции с наибольшими расхождениями
        df_sorted = df.sort_values('Разница_абсолютная', ascending=False)
        
        print(f"\nТоп-20 номенклатур с наибольшими разницами в остатках:")
        for i, (_, row) in enumerate(df_sorted.head(20).iterrows(), 1):
            if abs(row['Разница_кг']) > 0.001:
                print(f"{i:2d}. {row['Номенклатура']}: "
                      f"основной={row['Остаток_основной_отчет_кг']:.3f} кг, "
                      f"предварительный={row['Остаток_предварительный_отчет_кг']:.3f} кг, "
                      f"разница={row['Разница_кг']:.3f} кг")
        
        # Находим позиции с совпадающими остатками
        matching_balances = df[abs(df['Разница_кг']) < 0.001]
        print(f"\nНайдено {len(matching_balances)} номенклатур с совпадающими остатками (разница < 0.001 кг)")
        
        # Находим позиции, где разница больше 1 кг
        significant_differences = df[abs(df['Разница_кг']) > 1.0]
        print(f"Найдено {len(significant_differences)} номенклатур с разницей более 1 кг")
        
        # Сохраняем позиции с большими расхождениями в отдельный файл
        if not significant_differences.empty:
            significant_file = os.path.join(project_root, "результаты", "значительные_расхождения_остатков.csv")
            significant_differences.to_csv(significant_file, index=False, encoding='utf-8')
            print(f"Позиции со значительными расхождениями сохранены в файл: {significant_file}")
            
        # Анализируем позиции с нулевыми остатками в основном отчете
        zero_in_main = df[df['Остаток_основной_отчет_кг'] == 0.0]
        print(f"\nПозиций с нулевыми остатками в основном отчете: {len(zero_in_main)}")
        if not zero_in_main.empty:
            print("Примеры таких позиций:")
            for i, (_, row) in enumerate(zero_in_main.head(10).iterrows(), 1):
                print(f"  {i}. {row['Номенклатура']}: "
                      f"основной=0.000 кг, предварительный={row['Остаток_предварительный_отчет_кг']:.3f} кг")
        
        # Анализируем позиции с нулевыми остатками в предварительном отчете
        zero_in_prelim = df[df['Остаток_предварительный_отчет_кг'] == 0.0]
        print(f"\nПозиций с нулевыми остатками в предварительном отчете: {len(zero_in_prelim)}")
        if not zero_in_prelim.empty:
            print("Примеры таких позиций:")
            for i, (_, row) in enumerate(zero_in_prelim.head(10).iterrows(), 1):
                print(f"  {i}. {row['Номенклатура']}: "
                      f"основной={row['Остаток_основной_отчет_кг']:.3f} кг, предварительный=0.000 кг")
                      
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    detailed_balance_comparison()