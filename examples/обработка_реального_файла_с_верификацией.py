#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример обработки реального файла данных с верификацией точности коэффициентов усушки

Этот скрипт обрабатывает указанный файл данных и выполняет верификацию точности 
рассчитанных коэффициентов усушки.
"""

import sys
import os
import pandas as pd
import json

# Добавляем путь к папке src для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.shrinkage_system import ShrinkageSystem
from core.data_processor import DataProcessor
from core.shrinkage_verification_system import ShrinkageVerificationSystem


def process_real_file_with_verification(file_path):
    """Обрабатывает реальный файл данных с верификацией коэффициентов усушки."""
    print(f"🔍 Обработка файла: {file_path}")
    print("=" * 60)
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return
    
    try:
        # Создаем систему усушки с включенной верификацией
        system = ShrinkageSystem()
        # Включаем верификацию через конфигурацию
        system.config['enable_verification'] = True
        system.config['use_adaptive_model'] = True
        
        print("✅ Система усушки инициализирована")
        
        # Читаем файл Excel
        print("📖 Чтение файла Excel...")
        # Читаем файл без заголовков для анализа структуры
        df_raw = pd.read_excel(file_path, header=None)
        print(f"📊 Размер данных: {df_raw.shape[0]} строк, {df_raw.shape[1]} столбцов")
        
        # Попытка определить структуру данных
        # Ищем строки с номенклатурами (содержащие информацию о рыбе)
        product_rows = df_raw[
            df_raw[0].str.contains('РЫБА|СЕЛЬДЬ|СКУМБРИЯ|ЩУКА|ОКУНЬ|ГОРБУША|КЕТА|СЕМГА|ФОРЕЛЬ|ИКРА|КРЕВЕТКИ|МАСЛЕНАЯ|НЕРКА|МОЙВА|ЮКОЛА|ВОМЕР|БРЮШКИ|КОРЮШКА|ЛЕЩ|СИГ|ДОРАДО|БЕЛОРЫБИЦА|ТАРАНЬ|ЧЕХОНЬ|ПЕЛЯДЬ|ВОБЛА|КАМБАЛА|Х/К|Г/К|С/С', case=False, na=False) & 
            ~df_raw[0].str.contains('Ведомость|Параметры|Отбор|Склад|Номенклатура|Документ|Партия|Отчет|Приходная|Инвентаризация|Монетка рыба', case=False, na=False)
        ]
        
        print(f"🐟 Найдено продуктовых записей: {len(product_rows)}")
        
        if len(product_rows) == 0:
            print("⚠️  Продуктовые записи не найдены. Попытка альтернативного подхода...")
            # Попробуем другой подход - ищем строки с числовыми данными
            numeric_rows = df_raw.dropna(subset=[4, 6, 7, 8], how='all')
            if len(numeric_rows) > 0:
                product_rows = numeric_rows.head(20)  # Берем первые 20 строк для примера
                print(f"🔢 Используем первые {len(product_rows)} строк с числовыми данными")
        
        if len(product_rows) == 0:
            print("❌ Не удалось найти подходящие данные для обработки")
            return
        
        # Создаем структуру данных для обработки
        product_data = []
        
        # Обрабатываем найденные строки
        for index, row in product_rows.iterrows():
            try:
                # Получаем название номенклатуры
                nomenclature = str(row.iloc[0]) if len(row) > 0 else f"Номенклатура_{index}"
                
                # Извлекаем числовые значения (предполагаем стандартную структуру)
                # Столбцы: 0-Номенклатура, 4-Начальный остаток, 6-Приход, 7-Расход, 8-Конечный остаток
                initial_balance = pd.to_numeric(row.iloc[4], errors='coerce') if len(row) > 4 else 0.0
                incoming = pd.to_numeric(row.iloc[6], errors='coerce') if len(row) > 6 else 0.0
                outgoing = pd.to_numeric(row.iloc[7], errors='coerce') if len(row) > 7 else 0.0
                final_balance = pd.to_numeric(row.iloc[8], errors='coerce') if len(row) > 8 else 0.0
                
                # Проверяем, что значения существуют
                if pd.notna(initial_balance) and pd.notna(final_balance):
                    # Рассчитываем период хранения (примерно 7 дней как стандарт)
                    storage_days = 7
                    
                    # Создаем запись
                    product_data.append({
                        'Номенклатура': nomenclature,
                        'Начальный_остаток': initial_balance,
                        'Приход': incoming if pd.notna(incoming) else 0.0,
                        'Расход': outgoing if pd.notna(outgoing) else 0.0,
                        'Конечный_остаток': final_balance,
                        'Период_хранения_дней': storage_days
                    })
            except Exception as e:
                print(f"   ❌ Ошибка обработки строки {index}: {str(e)}")
                continue
        
        if len(product_data) == 0:
            print("❌ Не удалось извлечь данные о продуктах")
            return
        
        print(f"✅ Успешно извлечено записей: {len(product_data)}")
        
        # Преобразуем в DataFrame
        dataset = pd.DataFrame(product_data)
        print("\n📊 Пример извлеченных данных:")
        print(dataset.head().to_string())
        
        # Выполняем обработку с верификацией
        print("\n🧮 Расчет коэффициентов усушки с верификацией...")
        results = system.process_dataset(
            dataset=dataset,
            source_filename=os.path.basename(file_path),
            use_adaptive=True
        )
        
        # Проверяем результаты
        if results['status'] != 'success':
            print(f"❌ Ошибка обработки: {results.get('message', 'Неизвестная ошибка')}")
            return
        
        print("✅ Обработка завершена успешно!")
        
        # Выводим сводку
        summary = results.get('summary', {})
        print(f"\n📈 Сводка результатов:")
        print(f"   Обработано номенклатур: {summary.get('total_nomenclatures', 0)}")
        print(f"   Средняя точность: {summary.get('avg_accuracy', 0):.2f}%")
        print(f"   Ошибок: {summary.get('error_count', 0)}")
        
        # Проверяем результаты верификации
        coefficients = results.get('coefficients', [])
        print(f"\n🔍 Результаты верификации:")
        for i, coeff in enumerate(coefficients[:5]):  # Показываем первые 5 результатов
            nomenclature = coeff.get('Номенклатура', 'Неизвестная номенклатура')
            accuracy = coeff.get('Точность_R2', 0)
            verification = coeff.get('Верификация', {})
            
            if verification:
                verification_status = verification.get('verification_status', 'unknown')
                validation_status = verification.get('validation_status', {})
                overall_status = validation_status.get('overall_status', 'unknown')
                
                print(f"   {i+1}. {nomenclature[:30]:30} | Точность: {accuracy:6.2f}% | Верификация: {overall_status.upper()}")
            else:
                print(f"   {i+1}. {nomenclature[:30]:30} | Точность: {accuracy:6.2f}% | Верификация: НЕТ ДАННЫХ")
        
        # Сохраняем результаты
        output_dir = "результаты"
        os.makedirs(output_dir, exist_ok=True)
        
        # Сохраняем коэффициенты в JSON
        coefficients_file = os.path.join(output_dir, f"коэффициенты_усушки_{os.path.splitext(os.path.basename(file_path))[0]}_верификация.json")
        with open(coefficients_file, 'w', encoding='utf-8') as f:
            json.dump(coefficients, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Коэффициенты сохранены в: {coefficients_file}")
        
        # Сохраняем отчеты
        reports = results.get('reports', {})
        for report_name, report_content in reports.items():
            report_file = os.path.join(output_dir, f"{report_name}_верификация.html")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"💾 Отчет '{report_name}' сохранен в: {report_file}")
        
        print(f"\n🎉 Обработка файла завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке файла: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Путь к файлу данных
    file_path = r"C:\Users\D_909\Desktop\для нового проекта\исходные_данные\Для_расчета_коэфф\b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25.xls"
    
    # Обрабатываем файл
    process_real_file_with_verification(file_path)