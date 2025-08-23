import pandas as pd
import re
from typing import List, Dict, Tuple

def analyze_inventory_data_detailed(csv_file: str) -> None:
    """
    Подробный анализ данных из CSV файла для выявления дубликатов номенклатур,
    повторяя логику из parse_inventory_data_improved.
    """
    try:
        df = pd.read_csv(csv_file, header=None, dtype=str)
        if df.empty:
            print("Файл CSV пуст")
            return
    except Exception as e:
        print(f"Ошибка чтения CSV файла: {str(e)}")
        return
    
    nomenclature_data = []
    group_data = []
    current_nomenclature = None
    current_summary = None
    current_documents = []
    line_number = 0

    def save_current_nomenclature():
        nonlocal current_nomenclature, current_summary, current_documents, nomenclature_data, group_data
        if current_nomenclature and current_summary:
            if not current_documents:
                group_data.append(current_nomenclature)
                print(f"Добавлена в group_data: {current_nomenclature}")
            else:
                nomenclature_data.append({
                    'name': current_nomenclature,
                    'summary': current_summary,
                    'documents': current_documents
                })
                print(f"Добавлена в nomenclature_data: {current_nomenclature}")

    for idx, row in df.iterrows():
        line_number = idx + 1
        row_str = str(row[0]) if pd.notna(row[0]) else ""
        
        is_new_nomenclature = re.match(r'^[А-ЯЁ\s\(\)\"\.\/]+$', row_str.strip()) and len(row_str.strip()) > 3 and pd.isna(row[1])

        if is_new_nomenclature:
            print(f"Строка {line_number}: Найдена новая номенклатура: {row_str.strip()}")
            save_current_nomenclature()
            
            current_nomenclature = row_str.strip()
            current_summary = None
            current_documents = []
            print(f"  Установлена как текущая номенклатура: {current_nomenclature}")
            
            # Поиск summary
            for i in range(idx + 1, min(idx + 15, len(df))):
                next_row = df.iloc[i]
                if pd.notna(next_row[4]) and pd.notna(next_row[8]):
                    try:
                        initial = float(str(next_row[4]).replace(',', '.'))
                        income = float(str(next_row[6]).replace(',', '.')) if pd.notna(next_row[6]) else 0
                        expense = float(str(next_row[7]).replace(',', '.')) if pd.notna(next_row[7]) else 0
                        final = float(str(next_row[8]).replace(',', '.'))
                        
                        current_summary = {
                            'initial': initial,
                            'income': income,
                            'expense': expense,
                            'final': final
                        }
                        print(f"  Найден summary: {current_summary}")
                        break
                    except:
                        continue
        
        elif current_nomenclature and row_str.strip():
            if any(keyword in row_str for keyword in ['Отчет отдела', 'Приходная накладная', 'Инвентаризация', 'Списание', 'Перемещение', 'Пересортица']):
                current_documents.append({
                    'name': row_str.strip(),
                    'data': []
                })
                print(f"  Добавлен документ: {row_str.strip()}")
            elif re.match(r'\d{2}\.\d{2}\.\d{4}', row_str.strip()):
                if current_documents:
                    try:
                        values = []
                        for col in range(4, 9):
                            val_str = str(row[col]).replace(',', '.') if pd.notna(row[col]) and str(row[col]).strip() != '' else '0'
                            try:
                                values.append(float(val_str))
                            except (ValueError, IndexError):
                                values.append(0)
                        
                        current_documents[-1]['data'].append({
                            'date': row_str.strip(),
                            'values': values
                        })
                        print(f"  Добавлены данные в документ: {row_str.strip()}")
                    except:
                        continue
    
    # Сохранение последней номенклатуры
    save_current_nomenclature()
    
    # Подсчет дубликатов
    nomenclature_names = [item['name'] for item in nomenclature_data]
    name_counts = {}
    for name in nomenclature_names:
        if name in name_counts:
            name_counts[name] += 1
        else:
            name_counts[name] = 1
    
    # Вывод дубликатов
    print("\nАнализ дубликатов в nomenclature_data:")
    duplicates_found = False
    for name, count in name_counts.items():
        if count > 1:
            print(f"  {name}: {count} раз(а)")
            duplicates_found = True
    
    if not duplicates_found:
        print("  Дубликаты не найдены")
    
    print(f"\nВсего номенклатур в nomenclature_data: {len(nomenclature_data)}")
    print(f"Всего групп в group_data: {len(group_data)}")

if __name__ == "__main__":
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(project_root, "исходные_данные", "sheet_1_Лист_1.csv")
    print(f"Анализ файла: {csv_file}")
    print("=" * 50)
    analyze_inventory_data_detailed(csv_file)