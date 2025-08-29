#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальная верификация коэффициентов усушки с подробным анализом
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
from core.shrinkage_calculator import ShrinkageCalculator


def detailed_analysis(file_path):
    """Выполняет детальный анализ файла и верификацию коэффициентов."""
    print(f"🔍 Детальный анализ файла: {file_path}")
    print("=" * 70)
    
    # Читаем файл
    df = pd.read_excel(file_path, header=None)
    
    # Ищем заголовки
    header_row = None
    for i, row in df.iterrows():
        if 'Номенклатура' in str(row.iloc[0]) and 'Начальный остаток' in str(row.iloc[4]):
            header_row = i
            break
    
    if header_row is None:
        print("❌ Не удалось найти заголовки в файле")
        return
    
    print(f"📊 Заголовки найдены в строке {header_row}")
    
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
    
    # Анализируем данные
    print(f"\n📊 Анализ данных:")
    significant_shrinkage = 0
    zero_shrinkage = 0
    total_records = 0
    
    sample_data = []
    
    for index, row in product_data.iterrows():
        try:
            nomenclature = str(row.iloc[0])
            initial_balance = pd.to_numeric(row.iloc[4], errors='coerce')
            incoming = pd.to_numeric(row.iloc[6], errors='coerce')
            outgoing = pd.to_numeric(row.iloc[7], errors='coerce')
            final_balance = pd.to_numeric(row.iloc[8], errors='coerce')
            
            if pd.notna(initial_balance) and pd.notna(incoming) and pd.notna(outgoing) and pd.notna(final_balance):
                # Рассчитываем фактическую усушку
                theoretical_balance = initial_balance + incoming - outgoing
                actual_shrinkage = theoretical_balance - final_balance
                
                # Определяем значимость усушки
                if abs(actual_shrinkage) > 0.001:  # Значимая усушка (> 1 грамма)
                    significant_shrinkage += 1
                else:
                    zero_shrinkage += 1
                
                total_records += 1
                
                # Сохраняем примеры для анализа
                if len(sample_data) < 10:
                    sample_data.append({
                        'Номенклатура': nomenclature,
                        'Начальный': initial_balance,
                        'Приход': incoming,
                        'Расход': outgoing,
                        'Конечный': final_balance,
                        'Теоретический': theoretical_balance,
                        'Усушка': actual_shrinkage
                    })
        except Exception as e:
            continue
    
    print(f"   Всего записей: {total_records}")
    print(f"   С значимой усушкой: {significant_shrinkage}")
    print(f"   С нулевой усушкой: {zero_shrinkage}")
    
    print(f"\n📋 Примеры данных:")
    for i, data in enumerate(sample_data):
        print(f"   {i+1}. {data['Номенклатура'][:30]:30} | Усушка: {data['Усушка']:8.3f} кг")
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Подготавливаем данные для обработки (только с значимой усушкой)
    if significant_shrinkage > 0:
        print(f"\n🎯 Обработка записей с значимой усушкой...")
        
        processed_data = []
        for index, row in product_data.iterrows():
            try:
                nomenclature = str(row.iloc[0])
                initial_balance = pd.to_numeric(row.iloc[4], errors='coerce')
                incoming = pd.to_numeric(row.iloc[6], errors='coerce')
                outgoing = pd.to_numeric(row.iloc[7], errors='coerce')
                final_balance = pd.to_numeric(row.iloc[8], errors='coerce')
                
                if pd.notna(initial_balance) and pd.notna(incoming) and pd.notna(outgoing) and pd.notna(final_balance):
                    # Рассчитываем фактическую усушку
                    theoretical_balance = initial_balance + incoming - outgoing
                    actual_shrinkage = theoretical_balance - final_balance
                    
                    # Обрабатываем только записи с значимой усушкой
                    if abs(actual_shrinkage) > 0.001:
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
        
        if len(processed_data) > 0:
            # Преобразуем в DataFrame
            dataset = pd.DataFrame(processed_data)
            
            # Обрабатываем данные
            results = system.process_dataset(
                dataset=dataset,
                source_filename=os.path.basename(file_path),
                use_adaptive=True
            )
            
            if results['status'] == 'success':
                print("✅ Обработка завершена успешно!")
                
                # Анализируем результаты
                coefficients = results.get('coefficients', [])
                print(f"\n🔍 Результаты верификации ({len(coefficients)} записей):")
                
                verification_passed = 0
                verification_warning = 0
                verification_critical = 0
                
                for i, coeff in enumerate(coefficients):
                    nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
                    accuracy = coeff.get('Точность_R2', 0)
                    verification = coeff.get('Верификация', {})
                    
                    if verification:
                        verification_status = verification.get('verification_status', 'unknown')
                        validation_status = verification.get('validation_status', {})
                        overall_status = validation_status.get('overall_status', 'unknown')
                        
                        # Подсчитываем статусы
                        if overall_status == 'acceptable':
                            verification_passed += 1
                        elif overall_status == 'warning':
                            verification_warning += 1
                        elif overall_status == 'critical':
                            verification_critical += 1
                        
                        print(f"   {i+1:2d}. {nomenclature[:35]:35} | Точность: {accuracy:6.2f}% | Верификация: {overall_status.upper()}")
                    else:
                        print(f"   {i+1:2d}. {nomenclature[:35]:35} | Точность: {accuracy:6.2f}% | Верификация: НЕТ ДАННЫХ")
                
                print(f"\n📈 Статистика верификации:")
                print(f"   Успешно: {verification_passed}")
                print(f"   С предупреждениями: {verification_warning}")
                print(f"   Критические: {verification_critical}")
                
                # Сохраняем результаты
                output_dir = "результаты"
                os.makedirs(output_dir, exist_ok=True)
                
                coefficients_file = os.path.join(output_dir, f"детальные_коэффициенты_усушки_{os.path.splitext(os.path.basename(file_path))[0]}.json")
                with open(coefficients_file, 'w', encoding='utf-8') as f:
                    json.dump(coefficients, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
            else:
                print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
        else:
            print("❌ Нет записей с значимой усушкой для обработки")
    else:
        print("❌ В данных отсутствует значимая усушка для анализа")
        
        # Демонстрируем работу системы верификации с синтетическими данными
        print(f"\n🧪 Демонстрация системы верификации с синтетическими данными:")
        
        # Создаем систему верификации
        verification_system = ShrinkageVerificationSystem()
        
        # Пример синтетических данных с известной усушкой
        synthetic_data = {
            'name': 'Тестовая номенклатура',
            'initial_balance': 100.0,
            'incoming': 50.0,
            'outgoing': 30.0,
            'final_balance': 118.0,  # Усушка 2.0 кг
            'storage_days': 7
        }
        
        # Пример коэффициентов
        synthetic_coefficients = {
            'model_type': 'exponential',
            'coefficients': {
                'a': 0.02,   # 2% максимальная усушка
                'b': 0.05,   # Скорость достижения максимума
                'c': 0.001   # Линейный компонент
            },
            'r_squared': 0.92
        }
        
        print(f"   Исходные данные:")
        print(f"     Начальный баланс: {synthetic_data['initial_balance']} кг")
        print(f"     Приход: {synthetic_data['incoming']} кг")
        print(f"     Расход: {synthetic_data['outgoing']} кг")
        print(f"     Конечный баланс: {synthetic_data['final_balance']} кг")
        print(f"     Фактическая усушка: 2.000 кг")
        
        print(f"\n   Коэффициенты:")
        coeffs = synthetic_coefficients['coefficients']
        print(f"     a = {coeffs['a']:.4f}, b = {coeffs['b']:.4f}, c = {coeffs['c']:.4f}")
        print(f"     R² = {synthetic_coefficients['r_squared']:.4f}")
        
        # Выполняем верификацию
        verification_results = verification_system.verify_coefficients_accuracy(synthetic_data, synthetic_coefficients)
        
        if verification_results['verification_status'] == 'success':
            metrics = verification_results['accuracy_metrics']
            validation = verification_results['validation_status']
            
            print(f"\n   Результаты верификации:")
            print(f"     Прогнозируемая усушка: {metrics['predicted_shrinkage']:8.3f} кг")
            print(f"     Фактическая усушка:   {metrics['actual_shrinkage']:8.3f} кг")
            print(f"     R²:                   {metrics['r_squared']:8.4f}")
            print(f"     Статус:               {validation['overall_status'].upper()}")
            
            # Генерируем отчет
            report = verification_system.generate_verification_report(verification_results)
            print(f"\n📄 Отчет верификации:")
            print(report)


def main():
    """Основная функция."""
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    # Выполняем детальный анализ
    detailed_analysis(file_path)


if __name__ == "__main__":
    main()