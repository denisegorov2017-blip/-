#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ и обработка реального файла данных с верификацией точности коэффициентов усушки

Этот скрипт выполняет детальный анализ структуры файла и корректную обработку данных.
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


def analyze_file_structure(file_path):
    """Анализирует структуру файла и выводит информацию о данных."""
    print(f"🔍 Анализ структуры файла: {file_path}")
    print("=" * 60)
    
    # Читаем файл без заголовков
    df = pd.read_excel(file_path, header=None)
    print(f"📊 Общая структура файла:")
    print(f"   Строк: {df.shape[0]}, Столбцов: {df.shape[1]}")
    
    # Выводим первые 10 строк для понимания структуры
    print(f"\n📋 Первые 10 строк файла:")
    print(df.head(10).to_string())
    
    # Ищем строки с номенклатурами
    # Предполагаем, что номенклатуры содержат ключевые слова
    keywords = ['РЫБА', 'СЕЛЬДЬ', 'СКУМБРИЯ', 'ЩУКА', 'ОКУНЬ', 'ГОРБУША', 'КЕТА', 'СЕМГА', 
                'ФОРЕЛЬ', 'ИКРА', 'КРЕВЕТКИ', 'МАСЛЕНАЯ', 'НЕРКА', 'МОЙВА', 'ЮКОЛА', 'ВОМЕР',
                'БРЮШКИ', 'КОРЮШКА', 'ЛЕЩ', 'СИГ', 'ДОРАДО', 'БЕЛОРЫБИЦА', 'ТАРАНЬ', 'ЧЕХОНЬ',
                'ПЕЛЯДЬ', 'ВОБЛА', 'КАМБАЛА', 'Х/К', 'Г/К', 'С/С', 'ВЯЛЕН']
    
    product_mask = df[0].astype(str).str.contains('|'.join(keywords), case=False, na=False)
    product_rows = df[product_mask]
    
    print(f"\n🐟 Найдено строк с продуктами: {len(product_rows)}")
    
    if len(product_rows) > 0:
        print(f"\n📋 Примеры строк с продуктами:")
        print(product_rows.head().to_string())
    
    return df


def extract_product_data(df):
    """Извлекает данные о продуктах из DataFrame."""
    print(f"\n🔧 Извлечение данных о продуктах...")
    
    # Ищем строки с продуктами
    keywords = ['РЫБА', 'СЕЛЬДЬ', 'СКУМБРИЯ', 'ЩУКА', 'ОКУНЬ', 'ГОРБУША', 'КЕТА', 'СЕМГА', 
                'ФОРЕЛЬ', 'ИКРА', 'КРЕВЕТКИ', 'МАСЛЕНАЯ', 'НЕРКА', 'МОЙВА', 'ЮКОЛА', 'ВОМЕР',
                'БРЮШКИ', 'КОРЮШКА', 'ЛЕЩ', 'СИГ', 'ДОРАДО', 'БЕЛОРЫБИЦА', 'ТАРАНЬ', 'ЧЕХОНЬ',
                'ПЕЛЯДЬ', 'ВОБЛА', 'КАМБАЛА', 'Х/К', 'Г/К', 'С/С', 'ВЯЛЕН']
    
    product_mask = df[0].astype(str).str.contains('|'.join(keywords), case=False, na=False)
    product_rows = df[product_mask]
    
    product_data = []
    
    # Для каждой строки с продуктом пытаемся извлечь данные
    for index, row in product_rows.iterrows():
        try:
            # Номенклатура (первый столбец)
            nomenclature = str(row.iloc[0]) if len(row) > 0 else f"Номенклатура_{index}"
            
            # Пытаемся извлечь числовые данные
            # Предполагаем структуру: столбцы 4, 6, 7, 8 содержат данные
            initial_balance = pd.to_numeric(row.iloc[4], errors='coerce') if len(row) > 4 else np.nan
            incoming = pd.to_numeric(row.iloc[6], errors='coerce') if len(row) > 6 else np.nan
            outgoing = pd.to_numeric(row.iloc[7], errors='coerce') if len(row) > 7 else np.nan
            final_balance = pd.to_numeric(row.iloc[8], errors='coerce') if len(row) > 8 else np.nan
            
            # Проверяем, что все значения существуют
            if pd.notna(initial_balance) and pd.notna(incoming) and pd.notna(outgoing) and pd.notna(final_balance):
                # Рассчитываем фактическую усушку
                theoretical_balance = initial_balance + incoming - outgoing
                actual_shrinkage = theoretical_balance - final_balance
                
                product_data.append({
                    'Номенклатура': nomenclature,
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance,
                    'Фактическая_усушка': max(0, actual_shrinkage),  # Усушка не может быть отрицательной
                    'Период_хранения_дней': 7  # Стандартный период
                })
        except Exception as e:
            print(f"   ❌ Ошибка обработки строки {index}: {str(e)}")
            continue
    
    print(f"✅ Извлечено записей: {len(product_data)}")
    return product_data


def process_with_verification(product_data, file_name):
    """Обрабатывает данные с верификацией коэффициентов."""
    print(f"\n🧮 Обработка данных с верификацией...")
    
    if len(product_data) == 0:
        print("❌ Нет данных для обработки")
        return
    
    # Преобразуем в DataFrame
    dataset = pd.DataFrame(product_data)
    print(f"📊 Данные для обработки:")
    print(dataset.head().to_string())
    
    # Создаем систему усушки
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Обрабатываем данные
    results = system.process_dataset(
        dataset=dataset,
        source_filename=file_name,
        use_adaptive=True
    )
    
    if results['status'] != 'success':
        print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
        return
    
    print("✅ Обработка завершена успешно!")
    
    # Анализируем результаты верификации
    coefficients = results.get('coefficients', [])
    print(f"\n🔍 Результаты верификации ({len(coefficients)} записей):")
    
    verification_passed = 0
    verification_warning = 0
    verification_critical = 0
    
    for i, coeff in enumerate(coefficients[:10]):  # Показываем первые 10 результатов
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
            
            print(f"   {i+1:2d}. {nomenclature[:30]:30} | Точность: {accuracy:6.2f}% | Верификация: {overall_status.upper()}")
        else:
            print(f"   {i+1:2d}. {nomenclature[:30]:30} | Точность: {accuracy:6.2f}% | Верификация: НЕТ ДАННЫХ")
    
    print(f"\n📈 Статистика верификации:")
    print(f"   Успешно: {verification_passed}")
    print(f"   С предупреждениями: {verification_warning}")
    print(f"   Критические: {verification_critical}")
    
    # Сохраняем результаты
    output_dir = "результаты"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем коэффициенты в JSON
    coefficients_file = os.path.join(output_dir, f"коэффициенты_усушки_{os.path.splitext(file_name)[0]}_анализ.json")
    with open(coefficients_file, 'w', encoding='utf-8') as f:
        json.dump(coefficients, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
    
    # Сохраняем отчеты
    reports = results.get('reports', {})
    for report_name, report_content in reports.items():
        report_file = os.path.join(output_dir, f"{report_name}_анализ.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"💾 Отчет '{report_name}' сохранен в: {report_file}")


def main():
    """Основная функция."""
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    # Анализируем структуру файла
    df = analyze_file_structure(file_path)
    
    # Извлекаем данные о продуктах
    product_data = extract_product_data(df)
    
    if len(product_data) > 0:
        # Обрабатываем данные с верификацией
        file_name = os.path.basename(file_path)
        process_with_verification(product_data, file_name)
    else:
        print("❌ Не удалось извлечь данные о продуктах")


if __name__ == "__main__":
    main()