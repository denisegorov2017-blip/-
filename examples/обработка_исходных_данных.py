#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример обработки исходных данных для расчета коэффициентов усушки
"""

import sys
import os
import json
import pandas as pd

# Добавляем путь к папке src, чтобы можно было импортировать модули проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from shrinkage_project.adaptive_shrinkage_calculator import AdaptiveShrinkageModel
from shrinkage_project.data_models import NomenclatureRow

def process_source_data():
    """Обработка исходных данных для расчета коэффициентов усушки."""
    print("🔍 Обработка исходных данных для расчета коэффициентов усушки")
    print("=" * 60)
    
    # Путь к папке с исходными данными
    source_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../исходные_данные/Для_расчета_коэфф'))
    
    # Проверяем наличие папки с исходными данными
    if not os.path.exists(source_data_dir):
        print(f"❌ Папка с исходными данными не найдена: {source_data_dir}")
        return
    
    print(f"📂 Папка с исходными данными: {source_data_dir}")
    
    # Ищем Excel файлы в папке
    excel_files = [f for f in os.listdir(source_data_dir) if f.endswith('.xlsx')]
    
    if not excel_files:
        print("❌ В папке не найдено Excel файлов")
        return
    
    print(f"📊 Найдено Excel файлов: {len(excel_files)}")
    
    # Создаем адаптивную модель
    model = AdaptiveShrinkageModel()
    
    # Обрабатываем каждый файл
    for excel_file in excel_files:
        print(f"\n📄 Обработка файла: {excel_file}")
        file_path = os.path.join(source_data_dir, excel_file)
        
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path)
            print(f"   Загружено строк: {len(df)}")
            
            # Проверяем наличие необходимых столбцов
            required_columns = ['Номенклатура', 'Начальный остаток', 'Приход', 'Расход', 'Конечный остаток', 'Период хранения (дней)']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"   ❌ Отсутствуют необходимые столбцы: {missing_columns}")
                continue
            
            # Результаты для текущего файла
            file_results = {
                "source_file": excel_file,
                "total_rows": len(df),
                "product_types": {},
                "calculations": []
            }
            
            # Обрабатываем каждую строку
            for index, row in df.iterrows():
                try:
                    # Создаем объект валидации данных
                    nomenclature_data = NomenclatureRow(
                        Номенклатура=row['Номенклатура'],
                        Начальный_остаток=row['Начальный остаток'],
                        Приход=row['Приход'],
                        Расход=row['Расход'],
                        Конечный_остаток=row['Конечный остаток'],
                        Период_хранения_дней=row['Период хранения (дней)']
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
                    
                    # Рассчитываем фактическую усушку
                    actual_shrinkage = (nomenclature_data.initial_balance + nomenclature_data.incoming - 
                                      nomenclature_data.outgoing - nomenclature_data.final_balance)
                    actual_shrinkage_percent = (actual_shrinkage / nomenclature_data.initial_balance) * 100 if nomenclature_data.initial_balance > 0 else 0
                    
                    # Рассчитываем прогнозируемую усушку в процентах
                    forecast_percent = (forecast / nomenclature_data.initial_balance) * 100 if nomenclature_data.initial_balance > 0 else 0
                    
                    print(f"   {nomenclature_data.name:20} | Тип: {product_type_desc:15} | "
                          f"Факт: {actual_shrinkage_percent:.2f}% | Прогноз: {forecast_percent:.2f}%")
                    
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
                        "actual_shrinkage": actual_shrinkage,
                        "actual_shrinkage_percent": actual_shrinkage_percent,
                        "forecast_shrinkage": forecast,
                        "forecast_shrinkage_percent": forecast_percent,
                        "coefficients": coefficients
                    })
                    
                except Exception as e:
                    print(f"   ❌ Ошибка обработки строки {index + 1}: {str(e)}")
                    continue
            
            # Сохраняем результаты в JSON файл
            results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../результаты'))
            os.makedirs(results_dir, exist_ok=True)
            
            output_file = os.path.join(results_dir, f"результаты_обработки_{excel_file.replace('.xlsx', '.json')}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_results, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 Результаты сохранены в: {output_file}")
            
        except Exception as e:
            print(f"   ❌ Ошибка обработки файла {excel_file}: {str(e)}")
            continue
    
    print(f"\n✅ Обработка завершена!")

if __name__ == "__main__":
    process_source_data()