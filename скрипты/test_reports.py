import pandas as pd
import os
from bs4 import BeautifulSoup

def test_reports_integrity():
    """Тест проверяет целостность отчетов"""
    print("=== Тест целостности отчетов ===")
    
    # Пути к файлам
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_results_file = os.path.join(project_root, "результаты", "коэффициенты_усушки_улучшенные.csv")
    html_failures_file = os.path.join(project_root, "результаты", "необработанные_позиции.html")
    
    # Проверка существования файлов
    if not os.path.exists(csv_results_file):
        print(f"Ошибка: Файл с результатами не найден: {csv_results_file}")
        return False
    
    if not os.path.exists(html_failures_file):
        print(f"Ошибка: Файл с необработанными позициями не найден: {html_failures_file}")
        return False
    
    # Чтение основного отчета
    try:
        df_results = pd.read_csv(csv_results_file)
        print(f"Прочитан основной отчет: {len(df_results)} строк")
    except Exception as e:
        print(f"Ошибка чтения основного отчета: {str(e)}")
        return False
    
    # Проверка на дубликаты в основном отчете
    duplicated_results = df_results[df_results.duplicated('Номенклатура', keep=False)]
    if not duplicated_results.empty:
        print("Найдены дубликаты в основном отчете:")
        for _, row in duplicated_results.iterrows():
            print(f"  - {row['Номенклатура']}")
        return False
    else:
        print("Дубликатов в основном отчете не найдено")
    
    # Извлечение номенклатур из основного отчета
    successful_nomenclatures = set(df_results['Номенклатура'].tolist())
    print(f"Успешно обработанных номенклатур: {len(successful_nomenclatures)}")
    
    # Чтение отчета об ошибках
    try:
        with open(html_failures_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Ошибка чтения отчета об ошибках: {str(e)}")
        return False
    
    # Парсинг HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Извлечение номенклатур с ошибками
    failed_nomenclatures = set()
    failed_table = soup.find('table', {'id': 'failed-table'})
    if failed_table:
        rows = failed_table.find_all('tr')[1:]  # Пропускаем заголовок
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                nomenclature = cells[1].get_text(strip=True)
                failed_nomenclatures.add(nomenclature)
    
    print(f"Номенклатур с ошибками: {len(failed_nomenclatures)}")
    
    # Проверка пересечения множеств
    intersection = successful_nomenclatures.intersection(failed_nomenclatures)
    if intersection:
        print("Найдены номенклатуры, которые одновременно в результатах и в ошибках:")
        for item in intersection:
            print(f"  - {item}")
        return False
    else:
        print("Нет пересечений между успешно обработанными и необработанными позициями")
    
    # Проверка, что все номенклатуры из исходного файла учтены
    # Для этого нам нужно знать общее количество номенклатур в исходном файле
    # Мы можем получить это из логов или из самого исходного файла
    # Пока просто проверим, что нет явных противоречий
    
    print("Тест целостности отчетов пройден успешно!")
    return True

def test_data_structure():
    """Тест проверяет структуру исходных данных"""
    print("\n=== Тест структуры исходных данных ===")
    
    # Пути к файлам
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_source_file = os.path.join(project_root, "исходные_данные", "sheet_1_Лист_1.csv")
    
    # Проверка существования файла
    if not os.path.exists(csv_source_file):
        print(f"Ошибка: Исходный файл не найден: {csv_source_file}")
        return False
    
    # Чтение исходного файла
    try:
        df_source = pd.read_csv(csv_source_file, header=None, dtype=str)
        print(f"Прочитан исходный файл: {len(df_source)} строк")
    except Exception as e:
        print(f"Ошибка чтения исходного файла: {str(e)}")
        return False
    
    # Анализ структуры данных
    nomenclature_count = 0
    group_count = 0
    document_count = 0
    
    for idx, row in df_source.iterrows():
        row_str = str(row[0]) if pd.notna(row[0]) else ""
        
        # Проверка на номенклатуру (заглавные буквы, длина > 3, нет данных в следующих колонках)
        is_nomenclature = (
            row_str.strip() and 
            all(c.isupper() or c.isspace() or c in '()"/.' for c in row_str.strip()) and
            len(row_str.strip()) > 3 and 
            pd.isna(row[1])
        )
        
        if is_nomenclature:
            nomenclature_count += 1
            # Проверка следующих строк на наличие документов
            for i in range(idx + 1, min(idx + 15, len(df_source))):
                next_row = df_source.iloc[i]
                next_row_str = str(next_row[0]) if pd.notna(next_row[0]) else ""
                if any(keyword in next_row_str for keyword in ['Отчет отдела', 'Приходная накладная', 'Инвентаризация', 'Списание', 'Перемещение', 'Пересортица']):
                    document_count += 1
                    break
        
        # Проверка на группу (похоже на номенклатуру, но без документов)
        # Это сложнее определить без полного парсинга, поэтому пока пропустим
    
    print(f"Примерный подсчет:")
    print(f"  Номенклатур: {nomenclature_count}")
    print(f"  Документов: {document_count}")
    
    # Проверка, что есть данные для обработки
    if nomenclature_count == 0:
        print("Ошибка: В исходном файле не найдено номенклатур")
        return False
    
    print("Тест структуры исходных данных пройден успешно!")
    return True

def main():
    """Основная функция для запуска тестов"""
    print("Запуск тестов проверки отчетов")
    print("=" * 50)
    
    # Запуск тестов
    success1 = test_data_structure()
    success2 = test_reports_integrity()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("Все тесты пройдены успешно!")
    else:
        print("Некоторые тесты не пройдены. Проверьте вывод выше.")

if __name__ == "__main__":
    main()