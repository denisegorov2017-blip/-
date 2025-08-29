#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ данных из файла для поиска записей с реальной усушкой
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


def analyze_real_data_for_shrinkage(file_path):
    """Анализирует реальные данные для поиска записей с усушкой."""
    print(f"🔍 Анализ файла на наличие данных с усушкой: {file_path}")
    print("=" * 70)
    
    # Читаем файл
    try:
        df = pd.read_excel(file_path, header=None)
        print(f"✅ Файл успешно загружен")
        print(f"📊 Размер данных: {df.shape[0]} строк, {df.shape[1]} столбцов")
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {str(e)}")
        return
    
    # Ищем заголовки
    header_row = None
    for i, row in df.iterrows():
        if 'Номенклатура' in str(row.iloc[0]) and 'Начальный остаток' in str(row.iloc[4]):
            header_row = i
            break
    
    if header_row is None:
        print("❌ Не удалось найти заголовки в файле")
        # Попробуем альтернативный подход
        print("🔄 Попытка альтернативного анализа...")
        return analyze_without_headers(df, file_path)
    
    print(f"📊 Заголовки найдены в строке {header_row}")
    
    # Читаем данные с заголовками
    try:
        df_data = pd.read_excel(file_path, header=header_row)
        print(f"✅ Данные успешно загружены с заголовками")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {str(e)}")
        return
    
    # Фильтруем продукты
    keywords = ['РЫБА', 'СЕЛЬДЬ', 'СКУМБРИЯ', 'ЩУКА', 'ОКУНЬ', 'ГОРБУША', 'КЕТА', 'СЕМГА', 
                'ФОРЕЛЬ', 'ИКРА', 'КРЕВЕТКИ', 'МАСЛЕНАЯ', 'НЕРКА', 'МОЙВА', 'ЮКОЛА', 'ВОМЕР',
                'БРЮШКИ', 'КОРЮШКА', 'ЛЕЩ', 'СИГ', 'ДОРАДО', 'БЕЛОРЫБИЦА', 'ТАРАНЬ', 'ЧЕХОНЬ',
                'ПЕЛЯДЬ', 'ВОБЛА', 'КАМБАЛА', 'Х/К', 'Г/К', 'С/С', 'ВЯЛЕН']
    
    try:
        product_mask = df_data.iloc[:, 0].astype(str).str.contains('|'.join(keywords), case=False, na=False)
        product_data = df_data[product_mask]
        print(f"📊 Найдено продуктовых записей: {len(product_data)}")
    except Exception as e:
        print(f"❌ Ошибка фильтрации продуктов: {str(e)}")
        return
    
    # Анализируем данные на наличие усушки
    print(f"\n📊 Анализ данных на наличие усушки:")
    significant_shrinkage_items = []
    zero_shrinkage_items = []
    
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
                
                # Определяем значимость усушки (более 10 граммов)
                if abs(actual_shrinkage) > 0.01:
                    significant_shrinkage_items.append({
                        'nomenclature': nomenclature,
                        'initial_balance': initial_balance,
                        'incoming': incoming,
                        'outgoing': outgoing,
                        'final_balance': final_balance,
                        'theoretical_balance': theoretical_balance,
                        'actual_shrinkage': actual_shrinkage
                    })
                else:
                    zero_shrinkage_items.append({
                        'nomenclature': nomenclature,
                        'initial_balance': initial_balance,
                        'incoming': incoming,
                        'outgoing': outgoing,
                        'final_balance': final_balance,
                        'theoretical_balance': theoretical_balance,
                        'actual_shrinkage': actual_shrinkage
                    })
        except Exception as e:
            continue
    
    print(f"   Записей с значимой усушкой: {len(significant_shrinkage_items)}")
    print(f"   Записей с нулевой усушкой: {len(zero_shrinkage_items)}")
    
    # Показываем примеры с значимой усушкой
    if significant_shrinkage_items:
        print(f"\n📋 Примеры записей с значимой усушкой:")
        for i, item in enumerate(significant_shrinkage_items[:10]):
            print(f"   {i+1}. {item['nomenclature'][:40]:40} | Усушка: {item['actual_shrinkage']:8.3f} кг")
    else:
        print(f"\n⚠️  В файле не найдено записей с значимой усушкой")
        print(f"   Это может означать, что данные корректны и усушка минимальна")
    
    # Если есть записи с усушкой, обрабатываем их
    if significant_shrinkage_items:
        process_items_with_shrinkage(significant_shrinkage_items, file_path)
    else:
        print(f"\n🔍 Демонстрация работы системы с синтетическими данными:")
        demonstrate_with_synthetic_data()


def analyze_without_headers(df, file_path):
    """Анализ данных без заголовков."""
    print(f"🔍 Анализ данных без заголовков...")
    
    # Ищем строки с данными
    data_rows = []
    for index, row in df.iterrows():
        # Проверяем, есть ли числовые данные в нужных столбцах
        try:
            col4 = pd.to_numeric(row.iloc[4], errors='coerce')
            col6 = pd.to_numeric(row.iloc[6], errors='coerce')
            col7 = pd.to_numeric(row.iloc[7], errors='coerce')
            col8 = pd.to_numeric(row.iloc[8], errors='coerce')
            
            if pd.notna(col4) and pd.notna(col6) and pd.notna(col7) and pd.notna(col8):
                # Проверяем, что это похоже на данные инвентаризации
                if col4 > 0 or col6 > 0 or col7 > 0 or col8 > 0:
                    data_rows.append({
                        'index': index,
                        'col0': str(row.iloc[0]) if len(row) > 0 else '',
                        'col4': col4,
                        'col6': col6,
                        'col7': col7,
                        'col8': col8
                    })
        except:
            continue
    
    print(f"📊 Найдено строк с числовыми данными: {len(data_rows)}")
    
    if data_rows:
        print(f"\n📋 Примеры строк с данными:")
        for i, row in enumerate(data_rows[:5]):
            print(f"   {i+1}. {row['col0'][:40]:40} | {row['col4']:8.3f} | {row['col6']:8.3f} | {row['col7']:8.3f} | {row['col8']:8.3f}")
    
    return data_rows


def process_items_with_shrinkage(items, file_path):
    """Обрабатывает записи с усушкой."""
    print(f"\n🧮 Обработка записей с усушкой...")
    
    # Подготавливаем данные для обработки
    processed_data = []
    for item in items:
        processed_data.append({
            'Номенклатура': item['nomenclature'],
            'Начальный_остаток': item['initial_balance'],
            'Приход': item['incoming'],
            'Расход': item['outgoing'],
            'Конечный_остаток': item['final_balance'],
            'Период_хранения_дней': 7  # Стандартный период
        })
    
    # Преобразуем в DataFrame
    dataset = pd.DataFrame(processed_data)
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Обрабатываем данные
    print(f"📊 Обработка {len(processed_data)} записей...")
    results = system.process_dataset(
        dataset=dataset,
        source_filename=os.path.basename(file_path),
        use_adaptive=True
    )
    
    if results['status'] == 'success':
        print("✅ Обработка завершена успешно!")
        
        # Анализируем результаты
        coefficients = results.get('coefficients', [])
        print(f"\n🔍 Результаты обработки:")
        
        for i, coeff in enumerate(coefficients[:5]):  # Показываем первые 5 результатов
            nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
            accuracy = coeff.get('Точность_R2', 0)
            model = coeff.get('Модель', 'Неизвестная')
            a_coeff = coeff.get('Коэф_a', 0)
            
            print(f"   {i+1}. {nomenclature[:40]:40} | R²: {accuracy:6.2f}% | a: {a_coeff:.6f}")
            
            # Проверяем верификацию
            verification = coeff.get('Верификация', {})
            if verification:
                validation_status = verification.get('validation_status', {})
                overall_status = validation_status.get('overall_status', 'unknown')
                metrics = verification.get('accuracy_metrics', {})
                
                print(f"      Верификация: {overall_status.upper()} | Прогноз: {metrics.get('predicted_shrinkage', 0):.3f} кг")
            else:
                print(f"      Верификация: НЕТ ДАННЫХ")
        
        # Сохраняем результаты
        output_dir = "результаты"
        os.makedirs(output_dir, exist_ok=True)
        
        coefficients_file = os.path.join(output_dir, f"коэффициенты_усушки_с_анализом_{os.path.splitext(os.path.basename(file_path))[0]}.json")
        with open(coefficients_file, 'w', encoding='utf-8') as f:
            json.dump(coefficients, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
    else:
        print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")


def demonstrate_with_synthetic_data():
    """Демонстрирует работу системы с синтетическими данными."""
    print(f"\n🧪 Демонстрация работы системы с синтетическими данными:")
    
    # Создаем систему верификации
    verification_system = ShrinkageVerificationSystem()
    
    # Пример синтетических данных с известной усушкой
    synthetic_data = {
        'name': 'СИНТЕТИЧЕСКАЯ НОМЕНКЛАТУРА',
        'initial_balance': 100.0,
        'incoming': 50.0,
        'outgoing': 30.0,
        'final_balance': 118.5,  # Усушка 1.5 кг
        'storage_days': 7
    }
    
    # Пример коэффициентов
    synthetic_coefficients = {
        'model_type': 'exponential',
        'coefficients': {
            'a': 0.015,  # 1.5% максимальная усушка
            'b': 0.05,   # Скорость достижения максимума
            'c': 0.001   # Линейный компонент
        },
        'r_squared': 0.95
    }
    
    print(f"📊 Синтетические данные:")
    print(f"   Начальный баланс: {synthetic_data['initial_balance']} кг")
    print(f"   Приход: {synthetic_data['incoming']} кг")
    print(f"   Расход: {synthetic_data['outgoing']} кг")
    print(f"   Конечный баланс: {synthetic_data['final_balance']} кг")
    print(f"   Фактическая усушка: 1.500 кг")
    
    # Выполняем верификацию
    verification_results = verification_system.verify_coefficients_accuracy(synthetic_data, synthetic_coefficients)
    
    if verification_results['verification_status'] == 'success':
        metrics = verification_results['accuracy_metrics']
        validation = verification_results['validation_status']
        
        print(f"\n🔍 Результаты верификации:")
        print(f"   Прогнозируемая усушка: {metrics['predicted_shrinkage']:8.3f} кг")
        print(f"   Фактическая усушка:   {metrics['actual_shrinkage']:8.3f} кг")
        print(f"   R² верификации:       {metrics['r_squared']:8.4f}")
        print(f"   Статус:               {validation['overall_status'].upper()}")
        
        # Генерируем отчет
        report = verification_system.generate_verification_report(verification_results)
        print(f"\n📄 Отчет верификации:")
        print(report)


def main():
    """Основная функция."""
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    # Анализируем данные
    analyze_real_data_for_shrinkage(file_path)


if __name__ == "__main__":
    main()