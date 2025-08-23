
import pandas as pd
import argparse
import os

def compare_balances(file1, file2, output_file, mode='detailed'):
    """
    Сравнивает два CSV файла с остатками.

    Args:
        file1 (str): Путь к первому файлу.
        file2 (str): Путь ко второму файлу.
        output_file (str): Путь для сохранения результата.
        mode (str): Режим сравнения ('simple' или 'detailed').
    """
    try:
        df1 = pd.read_csv(file1, sep=';')
        df2 = pd.read_csv(file2, sep=';')

        # Простое сравнение (проверка наличия номенклатуры)
        if mode == 'simple':
            merged = pd.merge(df1, df2, on='Номенклатура', how='outer', indicator=True)
            in_file1_not_in_file2 = merged[merged['_merge'] == 'left_only']
            in_file2_not_in_file1 = merged[merged['_merge'] == 'right_only']
            
            result_df = pd.concat([
                in_file1_not_in_file1[['Номенклатура']].assign(Статус=f'Есть только в {os.path.basename(file1)}'),
                in_file2_not_in_file1[['Номенклатура']].assign(Статус=f'Есть только в {os.path.basename(file2)}')
            ])

        # Детальное сравнение (сравнение значений)
        elif mode == 'detailed':
            merged = pd.merge(df1, df2, on='Номенклатура', suffixes=('_1', '_2'), how='inner')
            
            # Предполагаем, что колонки для сравнения называются 'Начальный остаток'
            merged['Разница'] = merged['Начальный остаток_1'] - merged['Начальный остаток_2']
            
            result_df = merged[merged['Разница'] != 0]
            
        else:
            raise ValueError(f"Неизвестный режим сравнения: {mode}")

        result_df.to_csv(output_file, index=.False, sep=';', encoding='utf-8-sig')
        print(f"Результаты сравнения сохранены в: {output_file}")

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e.filename}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сравнение файлов с остатками.")
    parser.add_argument("--file1", required=True, help="Путь к первому файлу (эталон).")
    parser.add_argument("--file2", required=True, help="Путь ко второму файлу (расчет).")
    parser.add_argument("--output", required=True, help="Путь для сохранения файла с результатами.")
    parser.add_argument("--mode", default="detailed", choices=['simple', 'detailed'], help="Режим сравнения: 'simple' или 'detailed'.")
    
    args = parser.parse_args()
    
    compare_balances(args.file1, args.file2, args.output, args.mode)
