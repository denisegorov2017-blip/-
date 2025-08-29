#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ данных по номенклатуре "БЫЧКИ ВЯЛЕНЫЕ" из реального файла

Этот скрипт выполняет детальный анализ структуры файла и извлекает
все данные по номенклатуре "БЫЧКИ ВЯЛЕНЫЕ" для демонстрации процесса чтения.
"""

import sys
import os
import pandas as pd
import json

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


def analyze_file_structure():
    """Анализ структуры файла данных."""
    print("🔍 Анализ структуры файла данных")
    print("=" * 60)
    
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return None
    
    try:
        # 1. Чтение файла без заголовков для анализа структуры
        print("📖 Чтение файла для анализа структуры...")
        df_raw = pd.read_excel(file_path, header=None)
        print(f"📊 Размер файла: {df_raw.shape[0]} строк, {df_raw.shape[1]} столбцов")
        
        # 2. Вывод первых 15 строк для понимания структуры
        print(f"\n📋 Первые 15 строк файла:")
        print(df_raw.head(15).to_string())
        
        # 3. Поиск строк с заголовками
        print(f"\n🔍 Поиск заголовков...")
        header_row = None
        for i, row in df_raw.iterrows():
            # Проверяем, содержит ли строка ключевые слова заголовков
            row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
            if any(keyword in row_str.lower() for keyword in ['номенклатура', 'наименование', 'продукт']):
                header_row = i
                print(f"🎯 Заголовки найдены в строке {i}: {row_str[:100]}...")
                break
        
        # 4. Поиск строк с номенклатурами рыбы
        print(f"\n🔍 Поиск строк с рыбной продукцией...")
        fish_keywords = ['РЫБА', 'СЕЛЬДЬ', 'СКУМБРИЯ', 'ЩУКА', 'ОКУНЬ', 'ГОРБУША', 'КЕТА', 'СЕМГА', 
                        'ФОРЕЛЬ', 'ИКРА', 'КРЕВЕТКИ', 'МАСЛЕНАЯ', 'НЕРКА', 'МОЙВА', 'ЮКОЛА', 'ВОМЕР',
                        'БРЮШКИ', 'КОРЮШКА', 'ЛЕЩ', 'СИГ', 'ДОРАДО', 'БЕЛОРЫБИЦА', 'ТАРАНЬ', 'ЧЕХОНЬ',
                        'ПЕЛЯДЬ', 'ВОБЛА', 'КАМБАЛА', 'Х/К', 'Г/К', 'С/С', 'ВЯЛЕН', 'БЫЧКИ']
        
        product_mask = df_raw[0].astype(str).str.contains('|'.join(fish_keywords), case=False, na=False)
        product_rows = df_raw[product_mask]
        
        print(f"🐟 Найдено строк с рыбной продукцией: {len(product_rows)}")
        
        # 5. Поиск конкретно "БЫЧКИ ВЯЛЕНЫЕ"
        scomber_mask = df_raw[0].astype(str).str.contains('БЫЧКИ ВЯЛЕНЫЕ', case=False, na=False)
        scomber_rows = df_raw[scomber_mask]
        
        print(f"🎯 Найдено строк с 'БЫЧКИ ВЯЛЕНЫЕ': {len(scomber_rows)}")
        
        if len(scomber_rows) > 0:
            print(f"\n📄 Детали строк с 'БЫЧКИ ВЯЛЕНЫЕ':")
            for idx, row in scomber_rows.iterrows():
                print(f"   Строка {idx}:")
                for col_idx, cell in enumerate(row):
                    if pd.notna(cell):
                        print(f"     Столбец {col_idx}: {cell}")
                print()
        
        return df_raw, scomber_rows
        
    except Exception as e:
        print(f"❌ Ошибка при анализе структуры файла: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def extract_scomber_data(df_raw, scomber_rows):
    """Извлечение данных по 'БЫЧКИ ВЯЛЕНЫЕ'."""
    print("🔧 Извлечение данных по 'БЫЧКИ ВЯЛЕНЫЕ'")
    print("=" * 60)
    
    if len(scomber_rows) == 0:
        print("❌ Нет данных для извлечения")
        return []
    
    product_data = []
    
    for index, row in scomber_rows.iterrows():
        try:
            # Получаем название номенклатуры
            nomenclature = str(row.iloc[0]) if len(row) > 0 else f"Номенклатура_{index}"
            
            print(f"\n📄 Обработка строки {index}: {nomenclature}")
            
            # Извлекаем числовые значения из стандартных столбцов
            # Столбец 4 - Начальный остаток
            # Столбец 6 - Приход
            # Столбец 7 - Расход
            # Столбец 8 - Конечный остаток
            
            initial_balance = pd.to_numeric(row.iloc[4], errors='coerce') if len(row) > 4 else None
            incoming = pd.to_numeric(row.iloc[6], errors='coerce') if len(row) > 6 else None
            outgoing = pd.to_numeric(row.iloc[7], errors='coerce') if len(row) > 7 else None
            final_balance = pd.to_numeric(row.iloc[8], errors='coerce') if len(row) > 8 else None
            
            print(f"   Начальный остаток: {initial_balance}")
            print(f"   Приход: {incoming}")
            print(f"   Расход: {outgoing}")
            print(f"   Конечный остаток: {final_balance}")
            
            # Проверяем, что значения существуют
            if all(pd.notna(val) for val in [initial_balance, final_balance]):
                # Рассчитываем фактическую усушку
                theoretical_balance = initial_balance + (incoming if pd.notna(incoming) else 0) - (outgoing if pd.notna(outgoing) else 0)
                actual_shrinkage = theoretical_balance - final_balance
                
                print(f"   Теоретический баланс: {theoretical_balance:.3f}")
                print(f"   Фактическая усушка: {actual_shrinkage:.3f}")
                
                # Создаем запись
                product_data.append({
                    'Номенклатура': nomenclature,
                    'Начальный_остаток': float(initial_balance),
                    'Приход': float(incoming) if pd.notna(incoming) else 0.0,
                    'Расход': float(outgoing) if pd.notna(outgoing) else 0.0,
                    'Конечный_остаток': float(final_balance),
                    'Фактическая_усушка': max(0, float(actual_shrinkage)),  # Усушка не может быть отрицательной
                    'Период_хранения_дней': 7  # Стандартный период
                })
                
                print("   ✅ Данные успешно извлечены")
            else:
                print("   ⚠️  Недостаточно данных для извлечения")
                
        except Exception as e:
            print(f"   ❌ Ошибка обработки строки {index}: {str(e)}")
            continue
    
    return product_data


def save_analysis_results(product_data):
    """Сохранение результатов анализа."""
    print("💾 Сохранение результатов анализа")
    print("=" * 60)
    
    if len(product_data) == 0:
        print("❌ Нет данных для сохранения")
        return
    
    # Создаем директорию для результатов
    output_dir = "результаты"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем данные в JSON
    results_file = os.path.join(output_dir, "анализ_БЫЧКИ_ВЯЛЕНЫЕ.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Данные сохранены в: {results_file}")
    
    # Выводим сводку
    print(f"\n📊 Сводка по 'БЫЧКИ ВЯЛЕНЫЕ':")
    for i, data in enumerate(product_data):
        print(f"   {i+1}. {data['Номенклатура']}")
        print(f"      Начальный остаток: {data['Начальный_остаток']:.3f} кг")
        print(f"      Приход: {data['Приход']:.3f} кг")
        print(f"      Расход: {data['Расход']:.3f} кг")
        print(f"      Конечный остаток: {data['Конечный_остаток']:.3f} кг")
        print(f"      Фактическая усушка: {data['Фактическая_усушка']:.3f} кг")
        print()


def main():
    """Основная функция."""
    print("Анализ данных по номенклатуре 'БЫЧКИ ВЯЛЕНЫЕ'")
    print("=" * 70)
    
    # Анализируем структуру файла
    df_raw, scomber_rows = analyze_file_structure()
    
    if df_raw is None:
        return
    
    # Извлекаем данные
    product_data = extract_scomber_data(df_raw, scomber_rows)
    
    # Сохраняем результаты
    save_analysis_results(product_data)
    
    print("🎉 Анализ завершен!")


if __name__ == "__main__":
    main()