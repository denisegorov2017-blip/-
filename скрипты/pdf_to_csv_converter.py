import pdfplumber
import pandas as pd
import os

def extract_tables_from_pdf(pdf_path: str, csv_output_path: str):
    """
    Извлекает таблицы из PDF файла и сохраняет их в CSV.
    
    Args:
        pdf_path: Путь к PDF файлу
        csv_output_path: Путь к выходному CSV файлу
    """
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Извлекаем таблицы со страницы
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables):
                if table:  # Проверяем, что таблица не пустая
                    # Добавляем данные из таблицы
                    # Первая строка таблицы обычно содержит заголовки
                    # Но в нашем случае, мы просто добавим все строки
                    for row in table:
                        # Заменяем None на пустые строки для согласованности
                        cleaned_row = [cell if cell is not None else "" for cell in row]
                        all_data.append(cleaned_row)
    
    if all_data:
        # Создаем DataFrame и сохраняем в CSV
        # Мы не устанавливаем заголовки, так как структура данных может быть разной
        df = pd.DataFrame(all_data)
        df.to_csv(csv_output_path, index=False, header=False, encoding='utf-8')
        print(f"Данные успешно извлечены и сохранены в {csv_output_path}")
    else:
        print("Не удалось извлечь данные из PDF")

def main():
    """
    Основная функция для преобразования PDF в CSV.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Пути к файлам
        pdf_file = os.path.join(project_root, "исходные_данные", "Для_передварительной_усушки", "14,07,25- 21.07.25 Для предварительного расчета усушки.pdf")
        csv_output_file = os.path.join(project_root, "исходные_данные", "Для_передварительной_усушки", "sheet_1_Лист_1_prelim.csv")
        
        if not os.path.exists(pdf_file):
            print(f"PDF файл {pdf_file} не найден")
            return
            
        print(f"Начинаю преобразование PDF в CSV...")
        print(f"Исходный файл: {pdf_file}")
        
        extract_tables_from_pdf(pdf_file, csv_output_file)
        
    except Exception as e:
        print(f"Произошла ошибка при преобразовании PDF: {str(e)}")
        raise

if __name__ == "__main__":
    main()