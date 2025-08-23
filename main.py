
import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Основной скрипт для управления проектом.")
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    # Команда для расчета коэффициентов
    parser_calc = subparsers.add_parser('calculate', help='Запуск расчета коэффициентов усушки')
    parser_calc.add_argument('--input_file', type=str, help='Путь к входному файлу')
    parser_calc.add_argument('--calculation_start_date', type=str, help='Дата начала расчета (ГГГГ-ММ-ДД)')

    # Команда для сравнения остатков
    parser_compare = subparsers.add_parser('compare', help='Запуск сравнения остатков')
    parser_compare.add_argument("--file1", required=True, help="Путь к первому файлу (эталон).")
    parser_compare.add_argument("--file2", required=True, help="Путь ко второму файлу (расчет).")
    parser_compare.add_argument("--output", required=True, help="Путь для сохранения файла с результатами.")
    parser_compare.add_argument("--mode", default="detailed", choices=['simple', 'detailed'], help="Режим сравнения: 'simple' или 'detailed'.")

    # Команда для запуска GUI
    parser_gui = subparsers.add_parser('gui', help='Запуск графического интерфейса')

    args = parser.parse_args()

    if args.command == 'calculate':
        print("Запуск расчета коэффициентов...")
        cmd = ["python", "скрипты/coefficient_calculator.py"]
        if args.input_file:
            cmd.extend(["--input_file", args.input_file])
        if args.calculation_start_date:
            cmd.extend(["--calculation_start_date", args.calculation_start_date])
        subprocess.run(cmd)

    elif args.command == 'compare':
        print("Запуск сравнения остатков...")
        cmd = ["python", "balance_analyzer.py", 
               "--file1", args.file1, 
               "--file2", args.file2, 
               "--output", args.output, 
               "--mode", args.mode]
        subprocess.run(cmd)

    elif args.command == 'gui':
        print("Запуск графического интерфейса...")
        subprocess.run(["python", "скрипты/gui_tkinter.py"])

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
