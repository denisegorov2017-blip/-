#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример обработки реальных данных для расчета коэффициентов усушки
"""

import sys
import os
import json
import pandas as pd
import numpy as np

# Добавляем путь к папке src, чтобы можно было импортировать модули проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from shrinkage_project.adaptive_shrinkage_calculator import AdaptiveShrinkageModel
from shrinkage_project.data_models import NomenclatureRow

def extract_product_data_from_real_file(file_path):
    """Извлекает данные о продуктах из реального файла."""
    print(f"📝 Извлечение данных из файла: {file_path}")
    
    # Читаем файл без заголовков
    df = pd.read_excel(file_path, header=None)
    
    # Ищем строки с продуктами (содержат информацию о рыбе)
    product_rows = df[df[0].str.contains('РЫБА|СЕЛЬДЬ|СКУМБРИЯ|ЩУКА|ОКУНЬ|ГОРБУША|КЕТА|СЕМГА|ФОРЕЛЬ|ИКРА|КРЕВЕТКИ|МАСЛЕНАЯ|НЕРКА|МОЙВА|ЮКОЛА|ВОМЕР|БРЮШКИ|КОРЮШКА|ЛЕЩ|СИГ|ДОРАДО|БЕЛОРЫБИЦА|ТАРАНЬ|ЧЕХОНЬ|ПЕЛЯДЬ|ВОБЛА|КАМБАЛА|Х/К|Г/К|С/С', case=False, na=False) & 
                      ~df[0].str.contains('Ведомость|Параметры|Отбор|Склад|Номенклатура|Документ|Партия|Отчет|Приходная|Инвентаризация|Монетка рыба', case=False, na=False)]
    
    print(f"📊 Найдено продуктовых записей: {len(product_rows)}")
    
    # Создаем список для хранения данных
    product_data = []
    
    # Обрабатываем каждую строку с продуктами
    for index, row in product_rows.iterrows():
        try:
            # Получаем название номенклатуры
            nomenclature = str(row[0])
            
            # Извлекаем числовые значения
            initial_balance = pd.to_numeric(row[4], errors='coerce')
            incoming = pd.to_numeric(row[6], errors='coerce')
            outgoing = pd.to_numeric(row[7], errors='coerce')
            final_balance = pd.to_numeric(row[8], errors='coerce')
            
            # Проверяем, что значения существуют
            if pd.notna(initial_balance) and pd.notna(final_balance):
                # Рассчитываем период хранения (примерно 7 дней как в тестовых данных)
                storage_days = 7
                
                # Создаем запись
                product_data.append({
                    'Номенклатура': nomenclature,
                    'Начальный остаток': initial_balance,
                    'Приход': incoming if pd.notna(incoming) else 0.0,
                    'Расход': outgoing if pd.notna(outgoing) else 0.0,
                    'Конечный остаток': final_balance,
                    'Период хранения (дней)': storage_days
                })
        except Exception as e:
            print(f"   ❌ Ошибка обработки строки {index}: {str(e)}")
            continue
    
    print(f"✅ Успешно извлечено записей: {len(product_data)}")
    return product_data

def process_real_data():
    """Обработка реальных данных для расчета коэффициентов усушки."""
    print("🔍 Обработка реальных данных для расчета коэффициентов усушки")
    print("=" * 60)
    
    # Путь к папке с исходными данными
    source_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../исходные_данные/Для_расчета_коэфф'))
    
    # Проверяем наличие папки с исходными данными
    if not os.path.exists(source_data_dir):
        print(f"❌ Папка с исходными данными не найдена: {source_data_dir}")
        return
    
    print(f"📂 Папка с исходными данными: {source_data_dir}")
    
    # Ищем реальный файл данных (не пример)
    real_data_files = [f for f in os.listdir(source_data_dir) 
                      if f.endswith('.xls') and 'пример' not in f.lower()]
    
    if not real_data_files:
        print("❌ В папке не найдено файлов с реальными данными")
        return
    
    print(f"📊 Найдено файлов с реальными данными: {len(real_data_files)}")
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Обрабатываем каждый файл
    for data_file in real_data_files:
        print(f"\n📄 Обработка файла: {data_file}")
        file_path = os.path.join(source_data_dir, data_file)
        
        try:
            # Извлекаем данные о продуктах
            product_data = extract_product_data_from_real_file(file_path)
            
            if not product_data:
                print("   ❌ Не удалось извлечь данные о продуктах")
                continue
            
            # Результаты для текущего файла
            file_results = {
                "source_file": data_file,
                "total_rows": len(product_data),
                "product_types": {},
                "calculations": []
            }
            
            # Обрабатываем каждую запись
            for product in product_data[:10]:  # Обрабатываем только первые 10 записей для демонстрации
                try:
                    # Создаем объект валидации данных
                    nomenclature_data = NomenclatureRow(
                        Номенклатура=product['Номенклатура'],
                        Начальный_остаток=product['Начальный остаток'],
                        Приход=product['Приход'],
                        Расход=product['Расход'],
                        Конечный_остаток=product['Конечный остаток'],
                        Период_хранения_дней=product['Период хранения (дней)']
                    )
                    
                    # Определяем тип продукции
                    product_type = model.determine_product_type(nomenclature_data.name)
                    product_type_desc = {
                        'fish_fresh': 'Свежая рыба',
                        'fish_salt_cured': 'Слабосоленая рыба',
                        'fish_cold_smoked': 'Холодное копчение',
                        'fish_hot_smoked': 'Горячее копчение',
                        'fish_smoked': 'Копченая рыба',
                        'fish_dried': 'Сушеная/вяленая рыба'
                    }.get(product_type, 'Неизвестный тип')
                    
                    # Добавляем информацию о типе продукции
                    if product_type not in file_results["product_types"]:
                        file_results["product_types"][product_type] = {
                            "description": product_type_desc,
                            "count": 0
                        }
                    file_results["product_types"][product_type]["count"] += 1
                    
                    # Подготавливаем данные для адаптации
                    adaptation_data = {
                        'initial_balance': nomenclature_data.initial_balance,
                        'incoming': nomenclature_data.incoming,
                        'outgoing': nomenclature_data.outgoing,
                        'final_balance': nomenclature_data.final_balance,
                        'storage_days': nomenclature_data.storage_days
                    }
                    
                    # Адаптируем коэффициенты
                    coefficients = model.adapt_coefficients(
                        adaptation_data, 
                        nomenclature=nomenclature_data.name
                    )
                    
                    # Прогнозируем усушку
                    forecast = model.predict_with_adaptation(
                        nomenclature_data.storage_days, 
                        nomenclature=nomenclature_data.name
                    )
                    
                    # Анализируем недостачи из данных инвентаризации
                    # Документы инвентаризации содержат информацию о недостачах, 
                    # система анализирует их для определения части, связанной с усушкой
                    inventory_shortage = (nomenclature_data.initial_balance + nomenclature_data.incoming - 
                                        nomenclature_data.outgoing - nomenclature_data.final_balance)
                    
                    # Используем адаптивную модель для определения части недостач, связанной с усушкой
                    shrinkage_component = model.determine_shrinkage_component(
                        inventory_shortage, 
                        nomenclature_data.initial_balance,
                        nomenclature=nomenclature_data.name
                    )
                    
                    shrinkage_percent = (shrinkage_component / nomenclature_data.initial_balance) * 100 if nomenclature_data.initial_balance > 0 else 0
                    inventory_shortage_percent = (inventory_shortage / nomenclature_data.initial_balance) * 100 if nomenclature_data.initial_balance > 0 else 0
                    
                    # Рассчитываем прогнозируемую усушку в процентах
                    forecast_percent = (forecast / nomenclature_data.initial_balance) * 100 if nomenclature_data.initial_balance > 0 else 0
                    
                    print(f"   {nomenclature_data.name[:20]:20} | Тип: {product_type_desc:15} | "
                          f"Недостача: {inventory_shortage_percent:.2f}% | Усушка: {shrinkage_percent:.2f}% | Прогноз: {forecast_percent:.2f}%")
                    
                    # Сохраняем результаты
                    file_results["calculations"].append({
                        "nomenclature": nomenclature_data.name,
                        "product_type": product_type,
                        "product_type_description": product_type_desc,
                        "initial_balance": nomenclature_data.initial_balance,
                        "incoming": nomenclature_data.incoming,
                        "outgoing": nomenclature_data.outgoing,
                        "final_balance": nomenclature_data.final_balance,
                        "storage_days": nomenclature_data.storage_days,
                        "inventory_shortage": inventory_shortage,
                        "inventory_shortage_percent": inventory_shortage_percent,
                        "shrinkage_component": shrinkage_component,
                        "shrinkage_percent": shrinkage_percent,
                        "forecast_shrinkage": forecast,
                        "forecast_shrinkage_percent": forecast_percent,
                        "coefficients": coefficients
                    })
                    
                except Exception as e:
                    print(f"   ❌ Ошибка обработки продукта: {str(e)}")
                    continue
            
            # Сохраняем результаты в JSON файл
            results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../результаты'))
            os.makedirs(results_dir, exist_ok=True)
            
            output_file = os.path.join(results_dir, f"результаты_обработки_реальных_данных_{data_file.replace('.xls', '.json')}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_results, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 Результаты сохранены в: {output_file}")
            
        except Exception as e:
            print(f"   ❌ Ошибка обработки файла {data_file}: {str(e)}")
            continue
    
    print(f"\n✅ Обработка завершена!")

if __name__ == "__main__":
    process_real_data()