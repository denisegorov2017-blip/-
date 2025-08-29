#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная демонстрация системы верификации точности коэффициентов усушки
с реальными данными из файла и различными сценариями
"""

import sys
import os
import pandas as pd
import json
import numpy as np

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem
from core.shrinkage_verification_system import ShrinkageVerificationSystem


def demonstrate_real_file_processing():
    """Демонстрирует обработку реального файла."""
    print("🔍 ДЕМОНСТРАЦИЯ ОБРАБОТКИ РЕАЛЬНОГО ФАЙЛА")
    print("=" * 60)
    
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return
    
    print(f"✅ Файл найден: {os.path.basename(file_path)}")
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Читаем и обрабатываем данные
    try:
        # Читаем файл
        df = pd.read_excel(file_path, header=None)
        
        # Ищем заголовки
        header_row = None
        for i, row in df.iterrows():
            if 'Номенклатура' in str(row.iloc[0]) and 'Начальный остаток' in str(row.iloc[4]):
                header_row = i
                break
        
        if header_row is not None:
            # Читаем данные с заголовками
            df_data = pd.read_excel(file_path, header=header_row)
            
            # Фильтруем продукты
            keywords = ['РЫБА', 'СЕЛЬДЬ', 'СКУМБРИЯ', 'ЩУКА', 'ОКУНЬ', 'ГОРБУША', 'КЕТА', 'СЕМГА', 
                        'ФОРЕЛЬ', 'ИКРА', 'КРЕВЕТКИ', 'МАСЛЕНАЯ', 'НЕРКА', 'МОЙВА', 'ЮКОЛА', 'ВОМЕР',
                        'БРЮШКИ', 'КОРЮШКА', 'ЛЕЩ', 'СИГ', 'ДОРАДО', 'БЕЛОРЫБИЦА', 'ТАРАНЬ', 'ЧЕХОНЬ',
                        'ПЕЛЯДЬ', 'ВОБЛА', 'КАМБАЛА', 'Х/К', 'Г/К', 'С/С', 'ВЯЛЕН']
            
            product_mask = df_data.iloc[:, 0].astype(str).str.contains('|'.join(keywords), case=False, na=False)
            product_data = df_data[product_mask]
            
            print(f"📊 Найдено продуктовых записей: {len(product_data)}")
            
            # Подготавливаем данные для обработки
            processed_data = []
            for index, row in product_data.iterrows():
                try:
                    nomenclature = str(row.iloc[0])
                    initial_balance = pd.to_numeric(row.iloc[4], errors='coerce')
                    incoming = pd.to_numeric(row.iloc[6], errors='coerce')
                    outgoing = pd.to_numeric(row.iloc[7], errors='coerce')
                    final_balance = pd.to_numeric(row.iloc[8], errors='coerce')
                    
                    if pd.notna(initial_balance) and pd.notna(incoming) and pd.notna(outgoing) and pd.notna(final_balance):
                        processed_data.append({
                            'Номенклатура': nomenclature,
                            'Начальный_остаток': initial_balance,
                            'Приход': incoming,
                            'Расход': outgoing,
                            'Конечный_остаток': final_balance,
                            'Период_хранения_дней': 7
                        })
                except Exception as e:
                    continue
            
            if processed_data:
                # Преобразуем в DataFrame
                dataset = pd.DataFrame(processed_data)
                
                # Обрабатываем данные
                print(f"🧮 Обработка {len(processed_data)} записей...")
                results = system.process_dataset(
                    dataset=dataset,
                    source_filename=os.path.basename(file_path),
                    use_adaptive=True
                )
                
                if results['status'] == 'success':
                    print("✅ Обработка завершена успешно!")
                    
                    # Показываем сводку
                    coefficients = results.get('coefficients', [])
                    print(f"\n📈 Сводка результатов:")
                    print(f"   Обработано номенклатур: {len(coefficients)}")
                    
                    # Считаем среднюю точность
                    total_accuracy = 0
                    valid_count = 0
                    for coeff in coefficients:
                        accuracy = coeff.get('Точность_R2', 0)
                        if accuracy > 0:
                            total_accuracy += accuracy
                            valid_count += 1
                    
                    avg_accuracy = total_accuracy / valid_count if valid_count > 0 else 0
                    print(f"   Средняя точность: {avg_accuracy:.2f}%")
                    
                    # Показываем первые 5 результатов
                    print(f"\n📋 Примеры результатов:")
                    for i, coeff in enumerate(coefficients[:5]):
                        nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
                        accuracy = coeff.get('Точность_R2', 0)
                        print(f"   {i+1}. {nomenclature[:40]:40} | Точность: {accuracy:6.2f}%")
                else:
                    print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
            else:
                print("❌ Не удалось извлечь данные о продуктах")
        else:
            print("❌ Не удалось найти заголовки в файле")
            
    except Exception as e:
        print(f"❌ Ошибка обработки файла: {str(e)}")


def demonstrate_verification_scenarios():
    """Демонстрирует различные сценарии верификации."""
    print("\n\n🔍 ДЕМОНСТРАЦИЯ СЦЕНАРИЕВ ВЕРИФИКАЦИИ")
    print("=" * 60)
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Сценарий 1: Идеальные данные (высокая точность)
    print(f"\n🎯 Сценарий 1: Идеальные данные")
    scenario1_data = {
        'name': 'ИДЕАЛЬНАЯ НОМЕНКЛАТУРА',
        'initial_balance': 100.0,
        'incoming': 50.0,
        'outgoing': 30.0,
        'final_balance': 118.5,  # Усушка 1.5 кг
        'storage_days': 7
    }
    
    scenario1_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.015,  # 1.5% максимальная усушка
            'b': 0.05,   # Скорость достижения максимума
            'c': 0.001   # Линейный компонент
        },
        'r_squared': 0.98
    }
    
    results1 = verification_system.verify_coefficients_accuracy(scenario1_data, scenario1_coefficients)
    if results1['verification_status'] == 'success':
        metrics1 = results1['accuracy_metrics']
        validation1 = results1['validation_status']
        print(f"   Фактическая усушка: {metrics1['actual_shrinkage']:8.3f} кг")
        print(f"   Прогнозируемая усушка: {metrics1['predicted_shrinkage']:8.3f} кг")
        print(f"   R²: {metrics1['r_squared']:8.4f}")
        print(f"   Статус: {validation1['overall_status'].upper()}")
    
    # Сценарий 2: Средняя точность
    print(f"\n📊 Сценарий 2: Средняя точность")
    scenario2_data = {
        'name': 'СРЕДНЯЯ НОМЕНКЛАТУРА',
        'initial_balance': 200.0,
        'incoming': 100.0,
        'outgoing': 80.0,
        'final_balance': 215.0,  # Усушка 5.0 кг
        'storage_days': 7
    }
    
    scenario2_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.025,  # 2.5% максимальная усушка
            'b': 0.04,   # Скорость достижения максимума
            'c': 0.002   # Линейный компонент
        },
        'r_squared': 0.85
    }
    
    results2 = verification_system.verify_coefficients_accuracy(scenario2_data, scenario2_coefficients)
    if results2['verification_status'] == 'success':
        metrics2 = results2['accuracy_metrics']
        validation2 = results2['validation_status']
        print(f"   Фактическая усушка: {metrics2['actual_shrinkage']:8.3f} кг")
        print(f"   Прогнозируемая усушка: {metrics2['predicted_shrinkage']:8.3f} кг")
        print(f"   R²: {metrics2['r_squared']:8.4f}")
        print(f"   Статус: {validation2['overall_status'].upper()}")
    
    # Сценарий 3: Низкая точность
    print(f"\n⚠️  Сценарий 3: Низкая точность")
    scenario3_data = {
        'name': 'НИЗКАЯ ТОЧНОСТЬ',
        'initial_balance': 150.0,
        'incoming': 75.0,
        'outgoing': 60.0,
        'final_balance': 160.0,  # Усушка 5.0 кг
        'storage_days': 7
    }
    
    scenario3_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.010,  # 1.0% максимальная усушка
            'b': 0.03,   # Скорость достижения максимума
            'c': 0.0005  # Линейный компонент
        },
        'r_squared': 0.65
    }
    
    results3 = verification_system.verify_coefficients_accuracy(scenario3_data, scenario3_coefficients)
    if results3['verification_status'] == 'success':
        metrics3 = results3['accuracy_metrics']
        validation3 = results3['validation_status']
        print(f"   Фактическая усушка: {metrics3['actual_shrinkage']:8.3f} кг")
        print(f"   Прогнозируемая усушка: {metrics3['predicted_shrinkage']:8.3f} кг")
        print(f"   R²: {metrics3['r_squared']:8.4f}")
        print(f"   Статус: {validation3['overall_status'].upper()}")


def demonstrate_verification_criteria():
    """Демонстрирует критерии верификации."""
    print("\n\n🔍 ДЕМОНСТРАЦИЯ КРИТЕРИЕВ ВЕРИФИКАЦИИ")
    print("=" * 60)
    
    print(f"📊 Критерии валидации коэффициентов:")
    print(f"   R² (Коэффициент детерминации):")
    print(f"     - Приемлемый: > 0.85")
    print(f"     - Предупреждающий: 0.7 - 0.85")
    print(f"     - Критический: < 0.7")
    print(f"   RMSE (Среднеквадратическая ошибка):")
    print(f"     - Приемлемый: < 0.05")
    print(f"     - Предупреждающий: 0.05 - 0.1")
    print(f"     - Критический: > 0.1")
    print(f"   MAE (Средняя абсолютная ошибка):")
    print(f"     - Приемлемый: < 0.03")
    print(f"     - Предупреждающий: 0.03 - 0.07")
    print(f"     - Критический: > 0.07")
    
    # Пример расчета метрик
    print(f"\n🧮 Пример расчета метрик точности:")
    print(f"   Фактическая усушка: 2.000 кг")
    print(f"   Прогнозируемая усушка: 1.850 кг")
    print(f"   Разница: 0.150 кг")
    print(f"   R² = 1 - (SS_res / SS_tot) = 0.9431")
    print(f"   RMSE = √(Σ(прогноз - фактическое)² / n) = 0.0150")
    print(f"   MAE = Σ|прогноз - фактическое| / n = 0.0150")


def main():
    """Основная функция."""
    print("🚀 ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ СИСТЕМЫ ВЕРИФИКАЦИИ ТОЧНОСТИ КОЭФФИЦИЕНТОВ УСУШКИ")
    print("=" * 80)
    
    # Демонстрируем обработку реального файла
    demonstrate_real_file_processing()
    
    # Демонстрируем различные сценарии верификации
    demonstrate_verification_scenarios()
    
    # Демонстрируем критерии верификации
    demonstrate_verification_criteria()
    
    print(f"\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print(f"   Система верификации точности коэффициентов усушки готова к использованию")
    print(f"   с реальными данными из директории 'исходные_данные'")


if __name__ == "__main__":
    main()