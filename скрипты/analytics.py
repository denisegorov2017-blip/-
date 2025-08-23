import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json

def forecast_shrinkage(
    coefficients: Dict[str, float], 
    initial_mass: float, 
    days: int = 7,
    b_coef: float = 0.049
) -> Dict[str, float]:
    """
    Прогнозирование усушки на заданное количество дней.
    
    Args:
        coefficients: Словарь с коэффициентами {'a': float, 'b': float, 'c': float}
        initial_mass: Начальная масса товара (кг)
        days: Количество дней для прогноза (по умолчанию 7)
        b_coef: Коэффициент b (по умолчанию 0.049)
        
    Returns:
        Словарь с прогнозом усушки по дням и общую усушку
    """
    a = coefficients['a']
    b = coefficients.get('b', b_coef)  # Используем b из коэффициентов или значение по умолчанию
    c = coefficients.get('c', 0.0)
    
    # Рассчитываем усушку по дням
    daily_shrinkage = []
    cumulative_shrinkage = 0
    current_mass = initial_mass
    
    for day in range(1, days + 1):
        # Мгновенные потери при приемке
        if day == 1:
            instant_loss = c * current_mass
            cumulative_shrinkage += instant_loss
            current_mass -= instant_loss
            
        # Потери в течение дня
        day_loss = current_mass * a * b * np.exp(-b * day)
        cumulative_shrinkage += day_loss
        current_mass -= day_loss
        
        daily_shrinkage.append({
            'day': day,
            'shrinkage': day_loss,
            'cumulative_shrinkage': cumulative_shrinkage,
            'remaining_mass': current_mass
        })
    
    return {
        'daily_shrinkage': daily_shrinkage,
        'total_shrinkage': cumulative_shrinkage,
        'final_mass': current_mass
    }

def compare_coefficients(files: List[str]) -> pd.DataFrame:
    """
    Сравнение коэффициентов усушки по разным периодам/файлам.
    
    Args:
        files: Список путей к CSV файлам с коэффициентами
        
    Returns:
        DataFrame с сравнением коэффициентов
    """
    comparison_data = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден")
            continue
            
        try:
            df = pd.read_csv(file_path)
            # Извлекаем дату из имени файла или из столбца
            file_name = os.path.basename(file_path)
            period = file_name.replace('коэффициенты_усушки_', '').replace('.csv', '')
            
            for _, row in df.iterrows():
                comparison_data.append({
                    'nomenclature': row['Номенклатура'],
                    'period': period,
                    'a': row['a'],
                    'b': row['b (день⁻¹)'],
                    'c': row['c'],
                    'accuracy': row['Точность (%)'],
                    'date': row.get('Дата_расчета', '')
                })
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {str(e)}")
    
    if not comparison_data:
        return pd.DataFrame()
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Добавляем столбцы с изменением коэффициентов
    nomenclatures = comparison_df['nomenclature'].unique()
    changes_data = []
    
    for nom in nomenclatures:
        nom_data = comparison_df[comparison_df['nomenclature'] == nom].sort_values('period')
        if len(nom_data) < 2:
            continue
            
        # Берем первое и последнее значение для сравнения
        first_row = nom_data.iloc[0]
        last_row = nom_data.iloc[-1]
        
        changes_data.append({
            'nomenclature': nom,
            'a_change': last_row['a'] - first_row['a'],
            'b_change': last_row['b'] - first_row['b'],
            'c_change': last_row['c'] - first_row['c'],
            'accuracy_change': last_row['accuracy'] - first_row['accuracy'],
            'first_period': first_row['period'],
            'last_period': last_row['period']
        })
    
    changes_df = pd.DataFrame(changes_data)
    return changes_df

def cluster_nomenclatures(coefficients_file: str, n_clusters: int = 3) -> Dict:
    """
    Кластеризация номенклатур по коэффициентам усушки.
    
    Args:
        coefficients_file: Путь к CSV файлу с коэффициентами
        n_clusters: Количество кластеров (по умолчанию 3)
        
    Returns:
        Словарь с результатами кластеризации
    """
    if not os.path.exists(coefficients_file):
        raise ValueError(f"Файл {coefficients_file} не найден")
    
    try:
        df = pd.read_csv(coefficients_file)
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла: {str(e)}")
    
    if df.empty:
        raise ValueError("Файл с коэффициентами пуст")
    
    # Подготовка данных для кластеризации
    # Используем коэффициенты a, b, c
    feature_columns = ['a', 'b (день⁻¹)', 'c']
    features = df[feature_columns].copy()
    nomenclature_names = df['Номенклатура'].copy()
    
    # Удаление строк с NaN значениями и сохранение информации о необработанных позициях
    valid_mask = features.notna().all(axis=1)
    invalid_nomenclatures = nomenclature_names[~valid_mask].tolist()
    
    features = features[valid_mask]
    nomenclature_names = nomenclature_names[valid_mask]
    
    # Проверка, что остались данные для кластеризации
    if features.empty:
        raise ValueError("Нет данных для кластеризации после удаления строк с NaN значениями")
    
    # Ограничение количества кластеров, если данных недостаточно
    n_valid_samples = len(features)
    if n_valid_samples < n_clusters:
        # Если данных меньше, чем запрашиваемое количество кластеров,
        # уменьшаем количество кластеров до количества данных
        n_clusters = n_valid_samples
        if n_clusters == 0:
            raise ValueError("Нет данных для кластеризации")
    
    # Нормализация данных
    features_normalized = (features - features.mean()) / features.std()
    
    # Проверка на NaN после нормализации и заполнение их нулями
    # Это может произойти, если стандартное отклонение равно 0 (все значения в столбце одинаковы)
    if features_normalized.isna().any().any():
        features_normalized = features_normalized.fillna(0)
    
    # Применяем k-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(features_normalized)
    
    # Добавляем номер кластера в исходный DataFrame (только для валидных строк)
    df_clustered = pd.DataFrame({
        'Номенклатура': nomenclature_names,
        'cluster': clusters
    })
    
    # Подготавливаем результаты
    cluster_info = {}
    for i in range(n_clusters):
        cluster_nomenclatures_list = df_clustered[df_clustered['cluster'] == i]['Номенклатура'].tolist()
        cluster_center = kmeans.cluster_centers_[i]
        
        cluster_info[f'cluster_{i}'] = {
            'nomenclatures': cluster_nomenclatures_list,
            'center': {
                'a': cluster_center[0],
                'b': cluster_center[1],
                'c': cluster_center[2]
            },
            'count': len(cluster_nomenclatures_list)
        }
    
    return {
        'clusters': cluster_info,
        'n_clusters': n_clusters,
        'total_nomenclatures': len(df),
        'invalid_nomenclatures': invalid_nomenclatures
    }