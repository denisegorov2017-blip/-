#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация чтения и обработки отчета на примере номенклатуры "БЫЧКИ ВЯЛЕНЫЕ"

Этот скрипт показывает, как система читает реальные данные из Excel-файла,
находит конкретную номенклатуру и обрабатывает её для расчета коэффициентов усушки.
"""

import sys
import os
import pandas as pd
import json

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem


def demonstrate_report_reading():
    """Демонстрация процесса чтения отчета на примере "БЫЧКИ ВЯЛЕНЫЕ"."""
    print("🔍 Демонстрация чтения и обработки отчета")
    print("=" * 60)
    
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    print(f"📂 Работаем с файлом: {os.path.basename(file_path)}")
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return
    
    try:
        # 1. Чтение файла Excel
        print("\n📖 Этап 1: Чтение файла Excel...")
        # Читаем файл без заголовков для анализа структуры
        df_raw = pd.read_excel(file_path, header=None)
        print(f"📊 Размер данных: {df_raw.shape[0]} строк, {df_raw.shape[1]} столбцов")
        
        # 2. Поиск строк с номенклатурами
        print("\n🔍 Этап 2: Поиск строк с номенклатурами...")
        # Ищем строки, содержащие "БЫЧКИ ВЯЛЕНЫЕ"
        product_rows = df_raw[
            df_raw[0].astype(str).str.contains('БЫЧКИ ВЯЛЕНЫЕ', case=False, na=False)
        ]
        
        print(f"🎯 Найдено записей с 'БЫЧКИ ВЯЛЕНЫЕ': {len(product_rows)}")
        
        if len(product_rows) == 0:
            print("❌ Записи с 'БЫЧКИ ВЯЛЕНЫЕ' не найдены")
            # Попробуем найти похожие номенклатуры
            similar_rows = df_raw[
                df_raw[0].astype(str).str.contains('БЫЧКИ|ВЯЛЕНЫЕ', case=False, na=False)
            ]
            if len(similar_rows) > 0:
                print("📝 Похожие номенклатуры:")
                for idx, row in similar_rows.head(5).iterrows():
                    print(f"   - {row.iloc[0]}")
            return
        
        # 3. Анализ найденных строк
        print("\n📊 Этап 3: Анализ найденных строк...")
        product_data = []
        
        for index, row in product_rows.iterrows():
            try:
                # Получаем название номенклатуры
                nomenclature = str(row.iloc[0]) if len(row) > 0 else f"Номенклатура_{index}"
                
                print(f"\n📄 Строка {index}:")
                print(f"   Номенклатура: {nomenclature}")
                
                # Пытаемся извлечь числовые значения
                # Предполагаем структуру: столбцы 4, 6, 7, 8 содержат данные
                initial_balance = pd.to_numeric(row.iloc[4], errors='coerce') if len(row) > 4 else None
                incoming = pd.to_numeric(row.iloc[6], errors='coerce') if len(row) > 6 else None
                outgoing = pd.to_numeric(row.iloc[7], errors='coerce') if len(row) > 7 else None
                final_balance = pd.to_numeric(row.iloc[8], errors='coerce') if len(row) > 8 else None
                
                print(f"   Начальный остаток (столбец 4): {initial_balance}")
                print(f"   Приход (столбец 6): {incoming}")
                print(f"   Расход (столбец 7): {outgoing}")
                print(f"   Конечный остаток (столбец 8): {final_balance}")
                
                # Проверяем, что значения существуют
                if pd.notna(initial_balance) and pd.notna(final_balance):
                    # Рассчитываем фактическую усушку
                    theoretical_balance = initial_balance + (incoming if pd.notna(incoming) else 0) - (outgoing if pd.notna(outgoing) else 0)
                    actual_shrinkage = theoretical_balance - final_balance
                    
                    print(f"   Теоретический баланс: {theoretical_balance:.3f}")
                    print(f"   Фактическая усушка: {actual_shrinkage:.3f}")
                    
                    # Создаем запись для обработки
                    product_data.append({
                        'Номенклатура': nomenclature,
                        'Начальный_остаток': initial_balance,
                        'Приход': incoming if pd.notna(incoming) else 0.0,
                        'Расход': outgoing if pd.notna(outgoing) else 0.0,
                        'Конечный_остаток': final_balance,
                        'Период_хранения_дней': 7  # Стандартный период
                    })
                else:
                    print("   ⚠️  Недостаточно данных для расчета")
                    
            except Exception as e:
                print(f"   ❌ Ошибка обработки строки {index}: {str(e)}")
                continue
        
        # 4. Обработка данных системой расчета усушки
        if len(product_data) > 0:
            print(f"\n🧮 Этап 4: Обработка данных системой расчета усушки...")
            
            # Преобразуем в DataFrame
            dataset = pd.DataFrame(product_data)
            print("📊 Подготовленные данные для обработки:")
            print(dataset.to_string())
            
            # Создаем систему усушки
            system = ShrinkageSystem()
            system.config['use_adaptive_model'] = True
            
            # Обрабатываем данные
            results = system.process_dataset(
                dataset=dataset,
                source_filename=os.path.basename(file_path),
                use_adaptive=True
            )
            
            # Проверяем результаты
            if results['status'] == 'success':
                print("✅ Обработка завершена успешно!")
                
                # Выводим результаты
                coefficients = results.get('coefficients', [])
                print(f"\n🔍 Результаты расчета коэффициентов:")
                
                for i, coeff in enumerate(coefficients):
                    nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
                    accuracy = coeff.get('Точность_R2', 0)
                    a_coeff = coeff.get('a', 0)
                    b_coeff = coeff.get('b', 0)
                    c_coeff = coeff.get('c', 0)
                    
                    print(f"   {i+1}. {nomenclature}")
                    print(f"      Коэффициенты: a={a_coeff:.6f}, b={b_coeff:.6f}, c={c_coeff:.6f}")
                    print(f"      Точность (R²): {accuracy:.2f}%")
                
                # Сохраняем результаты
                output_dir = "результаты"
                os.makedirs(output_dir, exist_ok=True)
                
                coefficients_file = os.path.join(output_dir, f"коэффициенты_усушки_БЫЧКИ_ВЯЛЕНЫЕ.json")
                with open(coefficients_file, 'w', encoding='utf-8') as f:
                    json.dump(coefficients, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Результаты сохранены в: {coefficients_file}")
                
            else:
                print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
        else:
            print("❌ Нет данных для обработки")
            
    except Exception as e:
        print(f"❌ Ошибка при обработке файла: {str(e)}")
        import traceback
        traceback.print_exc()


def show_file_structure():
    """Показ структуры файла для понимания формата данных."""
    print("\n📋 Структура файла данных")
    print("=" * 60)
    
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return
    
    try:
        # Читаем первые 10 строк файла для понимания структуры
        df_preview = pd.read_excel(file_path, header=None, nrows=10)
        print("Предварительный просмотр первых 10 строк файла:")
        print(df_preview.to_string())
        
        # Пытаемся определить структуру заголовков
        print("\n🔍 Поиск заголовков...")
        for i, row in df_preview.iterrows():
            if 'Номенклатура' in str(row.iloc[0]) or 'номенклатура' in str(row.iloc[0]).lower():
                print(f"🎯 Заголовки найдены в строке {i}")
                print(f"   Содержание: {row.tolist()}")
                break
        else:
            print("ℹ️  Заголовки не найдены в первых 10 строках")
            
    except Exception as e:
        print(f"❌ Ошибка при анализе структуры файла: {str(e)}")


if __name__ == "__main__":
    print("Демонстрация процесса чтения и обработки отчета")
    print("=" * 70)
    
    # Показываем структуру файла
    show_file_structure()
    
    print("\n" + "=" * 70 + "\n")
    
    # Демонстрируем чтение отчета
    demonstrate_report_reading()