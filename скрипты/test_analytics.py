import pandas as pd
import os
import numpy as np
from analytics import forecast_shrinkage, compare_coefficients, cluster_nomenclatures

# Пути к файлам
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_output_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
html_output_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.html")
html_failures_output_file = os.path.join(project_root, "результаты", "необработанные_позиции.html")

def test_forecast_shrinkage():
    """Тестирование функции прогнозирования усушки"""
    print("=== Тестирование прогнозирования усушки ===")
    
    # Пример коэффициентов
    coefficients = {
        'a': 0.05,
        'b': 0.049,
        'c': 0.0
    }
    
    initial_mass = 100.0  # кг
    days = 7
    
    forecast_result = forecast_shrinkage(coefficients, initial_mass, days)
    
    print(f"Начальная масса: {initial_mass} кг")
    print(f"Период прогноза: {days} дней")
    print(f"Коэффициенты: a={coefficients['a']}, b={coefficients['b']}, c={coefficients['c']}")
    print("\nПрогноз по дням:")
    for day_data in forecast_result['daily_shrinkage']:
        print(f"  День {day_data['day']:2d}: "
              f"усушка {day_data['shrinkage']:8.3f} кг, "
              f"накопленная усушка {day_data['cumulative_shrinkage']:8.3f} кг, "
              f"остаток {day_data['remaining_mass']:8.3f} кг")
    
    print(f"\nОбщая усушка за {days} дней: {forecast_result['total_shrinkage']:.3f} кг")
    print(f"Масса после усушки: {forecast_result['final_mass']:.3f} кг")
    print()

def test_compare_coefficients():
    """Тестирование функции сравнения коэффициентов"""
    print("=== Тестирование сравнения коэффициентов ===")
    
    # Создадим временные файлы с тестовыми данными
    # Файл 1
    data1 = {
        'Номенклатура': ['Товар А', 'Товар Б'],
        'a': [0.05, 0.03],
        'b (день⁻¹)': [0.049, 0.049],
        'c': [0.0, 0.0],
        'Точность (%)': [95.0, 90.0],
        'Дата_расчета': ['01.08.25', '01.08.25']
    }
    df1 = pd.DataFrame(data1)
    temp_file1 = os.path.join(project_root, "результаты", "temp_coefficients_1.csv")
    df1.to_csv(temp_file1, index=False)
    
    # Файл 2
    data2 = {
        'Номенклатура': ['Товар А', 'Товар Б'],
        'a': [0.06, 0.04],
        'b (день⁻¹)': [0.049, 0.049],
        'c': [0.0, 0.0],
        'Точность (%)': [96.0, 92.0],
        'Дата_расчета': ['15.08.25', '15.08.25']
    }
    df2 = pd.DataFrame(data2)
    temp_file2 = os.path.join(project_root, "результаты", "temp_coefficients_2.csv")
    df2.to_csv(temp_file2, index=False)
    
    # Сравнение
    comparison_result = compare_coefficients([temp_file1, temp_file2])
    
    if not comparison_result.empty:
        print("Результаты сравнения:")
        print(comparison_result.to_string(index=False))
    else:
        print("Не удалось получить данные для сравнения")
    
    # Удаление временных файлов
    os.remove(temp_file1)
    os.remove(temp_file2)
    print()

def test_cluster_nomenclatures():
    """Тестирование функции кластеризации номенклатур"""
    print("=== Тестирование кластеризации номенклатур ===")
    
    # Создадим временный файл с тестовыми данными без NaN
    data = {
        'Номенклатура': ['Товар А', 'Товар Б', 'Товар В', 'Товар Г', 'Товар Д', 'Товар Е'],
        'a': [0.05, 0.06, 0.03, 0.04, 0.07, 0.02],
        'b (день⁻¹)': [0.049, 0.049, 0.049, 0.049, 0.049, 0.049],
        'c': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Точность (%)': [95.0, 96.0, 90.0, 92.0, 97.0, 88.0]
    }
    df = pd.DataFrame(data)
    temp_file = os.path.join(project_root, "результаты", "temp_coefficients_cluster.csv")
    df.to_csv(temp_file, index=False)
    
    # Кластеризация
    try:
        clustering_result = cluster_nomenclatures(temp_file, n_clusters=3)
        
        print(f"Общее количество номенклатур: {clustering_result['total_nomenclatures']}")
        print(f"Количество кластеров: {clustering_result['n_clusters']}")
        if 'invalid_nomenclatures' in clustering_result and clustering_result['invalid_nomenclatures']:
            print(f"Необработанные номенклатуры: {clustering_result['invalid_nomenclatures']}")
        print()
        
        for cluster_id, cluster_info in clustering_result['clusters'].items():
            print(f"КЛАСТЕР {cluster_id}:")
            print(f"  Количество номенклатур: {cluster_info['count']}")
            print(f"  Центр кластера:")
            print(f"    a = {cluster_info['center']['a']:.3f}")
            print(f"    b = {cluster_info['center']['b']:.3f}")
            print(f"    c = {cluster_info['center']['c']:.3f}")
            print(f"  Номенклатуры:")
            for nom in cluster_info['nomenclatures']:
                print(f"    - {nom}")
            print()
    except Exception as e:
        print(f"Ошибка при кластеризации: {str(e)}")
    
    # Удаление временного файла
    os.remove(temp_file)
    print()

def test_cluster_nomenclatures_with_real_data():
    """Тестирование функции кластеризации номенклатур с реальными данными"""
    print("=== Тестирование кластеризации номенклатур с реальными данными ===")
    
    if os.path.exists(csv_output_file):
        try:
            clustering_result = cluster_nomenclatures(csv_output_file, n_clusters=3)
            
            print(f"Общее количество номенклатур: {clustering_result['total_nomenclatures']}")
            print(f"Количество кластеров: {clustering_result['n_clusters']}")
            if 'invalid_nomenclatures' in clustering_result and clustering_result['invalid_nomenclatures']:
                print(f"Необработанные номенклатуры (содержат NaN значения):")
                for nom in clustering_result['invalid_nomenclatures'][:10]:  # Показываем первые 10
                    print(f"    - {nom}")
                if len(clustering_result['invalid_nomenclatures']) > 10:
                    print(f"    ... и еще {len(clustering_result['invalid_nomenclatures']) - 10} позиций")
            print()
            
            for cluster_id, cluster_info in clustering_result['clusters'].items():
                print(f"КЛАСТЕР {cluster_id}:")
                print(f"  Количество номенклатур: {cluster_info['count']}")
                print(f"  Центр кластера:")
                print(f"    a = {cluster_info['center']['a']:.3f}")
                print(f"    b = {cluster_info['center']['b']:.3f}")
                print(f"    c = {cluster_info['center']['c']:.3f}")
                print(f"  Номенклатуры (первые 10):")
                for nom in cluster_info['nomenclatures'][:10]:
                    print(f"    - {nom}")
                if len(cluster_info['nomenclatures']) > 10:
                    print(f"    ... и еще {len(cluster_info['nomenclatures']) - 10} позиций")
                print()
        except Exception as e:
            print(f"Ошибка при кластеризации: {str(e)}")
    else:
        print(f"Файл с результатами не найден: {csv_output_file}")
    print()

def main():
    """Основная функция для запуска тестов"""
    print("Тестирование аналитических функций")
    print("=" * 50)
    
    test_forecast_shrinkage()
    test_compare_coefficients()
    test_cluster_nomenclatures()
    test_cluster_nomenclatures_with_real_data()
    
    print("Тестирование завершено")

if __name__ == "__main__":
    main()