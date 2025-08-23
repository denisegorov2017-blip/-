import os
import sys
import pandas as pd

def test_data_processing():
    """Тест обработки данных"""
    # Получаем путь к проекту
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Путь к тестовым данным
    csv_file = os.path.join(project_root, "исходные_данные", "sheet_1_Лист_1.csv")
    
    print("Тест обработки данных")
    print("=" * 30)
    
    # Проверяем наличие файла
    if not os.path.exists(csv_file):
        print(f"Файл не найден: {csv_file}")
        return False
    
    print(f"Найден файл: {csv_file}")
    
    try:
        # Пытаемся прочитать файл
        df = pd.read_csv(csv_file, header=None, dtype=str, nrows=10)
        print(f"Успешно прочитано {len(df)} строк")
        print("Первые несколько строк:")
        print(df.head())
        return True
    except Exception as e:
        print(f"Ошибка чтения файла: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_data_processing()
    if success:
        print("\nТест пройден успешно!")
        sys.exit(0)
    else:
        print("\nТест не пройден!")
        sys.exit(1)