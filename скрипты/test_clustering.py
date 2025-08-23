import pandas as pd
import os
import numpy as np
from analytics import cluster_nomenclatures

# Пути к файлам
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_output_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")

def test_cluster_nomenclatures_no_nan():
    """Тестирование функции кластеризации номенклатур без NaN значений"""
    print("=== Тестирование кластеризации номенклатур без NaN значений ===")
    
    # Создадим временный файл с тестовыми данными без NaN
    data = {
        'Номенклатура': ['Товар А', 'Товар Б', 'Товар В', 'Товар Г', 'Товар Д', 'Товар Е'],
        'a': [0.05, 0.06, 0.03, 0.04, 0.07, 0.02],
        'b (день⁻¹)': [0.049, 0.049, 0.049, 0.049, 0.049, 0.049],
        'c': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Точность (%)': [95.0, 96.0, 90.0, 92.0, 97.0, 88.0]
    }
    df = pd.DataFrame(data)
    temp_file = os.path.join(project_root, "результаты", "temp_coefficients_cluster_no_nan.csv")
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
        import traceback
        traceback.print_exc()
    
    # Удаление временного файла
    if os.path.exists(temp_file):
        os.remove(temp_file)
    print()

def test_cluster_nomenclatures_with_nan():
    """Тестирование функции кластеризации номенклатур с NaN значениями"""
    print("=== Тестирование кластеризации номенклатур с NaN значениями ===")
    
    # Создадим временный файл с тестовыми данными с NaN
    data = {
        'Номенклатура': ['Товар А', 'Товар Б', 'Товар В', 'Товар Г', 'Товар Д', 'Товар Е', 'Товар Ж'],
        'a': [0.05, 0.06, np.nan, 0.04, 0.07, 0.02, 0.03],
        'b (день⁻¹)': [0.049, 0.049, 0.049, np.nan, 0.049, 0.049, 0.049],
        'c': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan],
        'Точность (%)': [95.0, 96.0, 90.0, 92.0, 97.0, 88.0, 91.0]
    }
    df = pd.DataFrame(data)
    temp_file = os.path.join(project_root, "результаты", "temp_coefficients_cluster_with_nan.csv")
    df.to_csv(temp_file, index=False)
    
    # Кластеризация
    try:
        clustering_result = cluster_nomenclatures(temp_file, n_clusters=3)
        
        print(f"Общее количество номенклатур: {clustering_result['total_nomenclatures']}")
        print(f"Количество кластеров: {clustering_result['n_clusters']}")
        if 'invalid_nomenclatures' in clustering_result and clustering_result['invalid_nomenclatures']:
            print(f"Необработанные номенклатуры (содержат NaN значения):")
            for nom in clustering_result['invalid_nomenclatures']:
                print(f"    - {nom}")
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
        import traceback
        traceback.print_exc()
    
    # Удаление временного файла
    if os.path.exists(temp_file):
        os.remove(temp_file)
    print()

def main():
    """Основная функция для запуска тестов"""
    print("Тестирование функции кластеризации")
    print("=" * 50)
    
    test_cluster_nomenclatures_no_nan()
    test_cluster_nomenclatures_with_nan()
    
    print("Тестирование завершено")

if __name__ == "__main__":
    main()