#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полная верификация реального файла данных с корректным расчетом усушки
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


def calculate_actual_shrinkage(row):
    """
    Рассчитывает фактическую усушку из данных строки.
    
    Args:
        row: Строка данных с балансом
        
    Returns:
        float: Фактическая усушка
    """
    try:
        initial_balance = float(row['Начальный_остаток'])
        incoming = float(row['Приход'])
        outgoing = float(row['Расход'])
        final_balance = float(row['Конечный_остаток'])
        
        # Теоретический баланс = начальный + приход - расход
        theoretical_balance = initial_balance + incoming - outgoing
        
        # Фактическая усушка = теоретический баланс - фактический конечный баланс
        actual_shrinkage = theoretical_balance - final_balance
        
        # Усушка не может быть отрицательной (это будет излишек)
        return max(0, actual_shrinkage)
    except (ValueError, KeyError, TypeError):
        return 0.0


def process_file_with_proper_verification(file_path):
    """Обрабатывает файл с правильной верификацией."""
    print(f"🔍 Обработка файла с верификацией: {file_path}")
    print("=" * 60)
    
    # Читаем файл
    df = pd.read_excel(file_path, header=None)
    
    # Ищем заголовки и данные
    # Ищем строку с названиями столбцов
    header_row = None
    for i, row in df.iterrows():
        if 'Номенклатура' in str(row.iloc[0]) and 'Начальный остаток' in str(row.iloc[4]):
            header_row = i
            break
    
    if header_row is None:
        print("❌ Не удалось найти заголовки в файле")
        return
    
    print(f"📊 Заголовки найдены в строке {header_row}")
    
    # Читаем файл с правильными заголовками
    df_data = pd.read_excel(file_path, header=header_row)
    
    # Фильтруем строки с продуктами
    keywords = ['РЫБА', 'СЕЛЬДЬ', 'СКУМБРИЯ', 'ЩУКА', 'ОКУНЬ', 'ГОРБУША', 'КЕТА', 'СЕМГА', 
                'ФОРЕЛЬ', 'ИКРА', 'КРЕВЕТКИ', 'МАСЛЕНАЯ', 'НЕРКА', 'МОЙВА', 'ЮКОЛА', 'ВОМЕР',
                'БРЮШКИ', 'КОРЮШКА', 'ЛЕЩ', 'СИГ', 'ДОРАДО', 'БЕЛОРЫБИЦА', 'ТАРАНЬ', 'ЧЕХОНЬ',
                'ПЕЛЯДЬ', 'ВОБЛА', 'КАМБАЛА', 'Х/К', 'Г/К', 'С/С', 'ВЯЛЕН']
    
    # Создаем маску для поиска продуктов
    product_mask = df_data.iloc[:, 0].astype(str).str.contains('|'.join(keywords), case=False, na=False)
    product_data = df_data[product_mask]
    
    print(f"📊 Найдено продуктовых записей: {len(product_data)}")
    
    if len(product_data) == 0:
        print("❌ Не найдено продуктовых записей")
        return
    
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
                # Рассчитываем фактическую усушку
                actual_shrinkage = calculate_actual_shrinkage({
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance
                })
                
                processed_data.append({
                    'Номенклатура': nomenclature,
                    'Начальный_остаток': initial_balance,
                    'Приход': incoming,
                    'Расход': outgoing,
                    'Конечный_остаток': final_balance,
                    'Фактическая_усушка': actual_shrinkage,
                    'Период_хранения_дней': 7
                })
        except Exception as e:
            print(f"   ❌ Ошибка обработки строки {index}: {str(e)}")
            continue
    
    print(f"✅ Подготовлено записей для обработки: {len(processed_data)}")
    
    if len(processed_data) == 0:
        print("❌ Нет данных для обработки")
        return
    
    # Преобразуем в DataFrame с правильными названиями столбцов
    dataset = pd.DataFrame(processed_data)
    dataset.columns = ['Номенклатура', 'Начальный_остаток', 'Приход', 'Расход', 'Конечный_остаток', 'Фактическая_усушка', 'Период_хранения_дней']
    
    print(f"\n📊 Пример данных для обработки:")
    print(dataset[['Номенклатура', 'Начальный_остаток', 'Приход', 'Расход', 'Конечный_остаток', 'Фактическая_усушка']].head().to_string())
    
    # Создаем систему усушки с включенной верификацией
    system = ShrinkageSystem()
    system.config['enable_verification'] = True
    system.config['use_adaptive_model'] = True
    
    # Обрабатываем данные
    print(f"\n🧮 Расчет коэффициентов усушки...")
    results = system.process_dataset(
        dataset=dataset,
        source_filename=os.path.basename(file_path),
        use_adaptive=True
    )
    
    if results['status'] != 'success':
        print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
        return
    
    print("✅ Обработка завершена успешно!")
    
    # Анализируем результаты
    coefficients = results.get('coefficients', [])
    print(f"\n🔍 Результаты обработки ({len(coefficients)} записей):")
    
    # Считаем статистику
    total_accuracy = 0
    valid_coefficients = 0
    
    for i, coeff in enumerate(coefficients[:15]):  # Показываем первые 15 результатов
        nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
        accuracy = coeff.get('Точность_R2', 0)
        verification = coeff.get('Верификация', {})
        
        # Считаем среднюю точность
        if accuracy > 0:
            total_accuracy += accuracy
            valid_coefficients += 1
        
        if verification:
            verification_status = verification.get('verification_status', 'unknown')
            validation_status = verification.get('validation_status', {})
            overall_status = validation_status.get('overall_status', 'unknown')
            
            print(f"   {i+1:2d}. {nomenclature[:35]:35} | Точность: {accuracy:6.2f}% | Верификация: {overall_status.upper()}")
        else:
            print(f"   {i+1:2d}. {nomenclature[:35]:35} | Точность: {accuracy:6.2f}% | Верификация: НЕТ ДАННЫХ")
    
    # Средняя точность
    avg_accuracy = total_accuracy / valid_coefficients if valid_coefficients > 0 else 0
    print(f"\n📈 Средняя точность коэффициентов: {avg_accuracy:.2f}%")
    
    # Сохраняем результаты
    output_dir = "результаты"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем коэффициенты
    coefficients_file = os.path.join(output_dir, f"коэффициенты_усушки_{os.path.splitext(os.path.basename(file_path))[0]}_верификация_полная.json")
    with open(coefficients_file, 'w', encoding='utf-8') as f:
        json.dump(coefficients, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
    
    # Сохраняем отчеты
    reports = results.get('reports', {})
    for report_name, report_content in reports.items():
        report_file = os.path.join(output_dir, f"{report_name}_верификация_полная.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"💾 Отчет '{report_name}' сохранен в: {report_file}")
    
    print(f"\n🎉 Полная обработка файла с верификацией завершена!")


def main():
    """Основная функция."""
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    # Обрабатываем файл
    process_file_with_proper_verification(file_path)


if __name__ == "__main__":
    main()