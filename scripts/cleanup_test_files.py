#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки файлов, созданных тестами
"""

import os
import shutil
import sys
from pathlib import Path
import glob
import argparse
import time
from datetime import datetime, timedelta

def cleanup_test_results(dry_run=False):
    """Очистка результатов тестов"""
    test_results_dir = Path("результаты/тестовые_данные")
    
    if not test_results_dir.exists():
        print("Директория с тестовыми результатами не найдена")
        return 0, 0
    
    # Счетчики для удаленных файлов
    deleted_files = 0
    deleted_dirs = 0
    
    # Удаляем все файлы в директории тестовых данных
    for item in test_results_dir.iterdir():
        try:
            if item.is_file():
                if not dry_run:
                    item.unlink()
                deleted_files += 1
                print(f"{'Будет удален' if dry_run else 'Удален'} файл: {item.name}")
            elif item.is_dir():
                if not dry_run:
                    shutil.rmtree(item)
                deleted_dirs += 1
                print(f"{'Будет удалена' if dry_run else 'Удалена'} директория: {item.name}")
        except Exception as e:
            print(f"Ошибка при удалении {item.name}: {e}")
    
    if not dry_run:
        print(f"Удалено файлов: {deleted_files}")
        print(f"Удалено директорий: {deleted_dirs}")
    else:
        print(f"Будет удалено файлов: {deleted_files}")
        print(f"Будет удалено директорий: {deleted_dirs}")
    
    return deleted_files, deleted_dirs

def cleanup_logs(dry_run=False, days_old=7):
    """Очистка логов старше указанного количества дней"""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("Директория с логами не найдена")
        return 0
    
    # Счетчики для удаленных файлов
    deleted_files = 0
    
    # Текущее время
    current_time = time.time()
    cutoff_time = current_time - (days_old * 24 * 60 * 60)
    
    # Удаляем логи старше указанного количества дней
    # Определяем лог-файлы по расширениям: .log, .log.zip
    log_extensions = ['.log', '.log.zip']
    
    for item in logs_dir.iterdir():
        try:
            if item.is_file():
                # Проверяем, является ли файл логом по расширению
                is_log_file = any(item.name.lower().endswith(ext) for ext in log_extensions)
                if is_log_file:
                    # Проверяем время последней модификации файла
                    file_modified = item.stat().st_mtime
                    if file_modified < cutoff_time:
                        if not dry_run:
                            item.unlink()
                        deleted_files += 1
                        print(f"{'Будет удален' if dry_run else 'Удален'} лог-файл старше {days_old} дней: {item.name}")
        except Exception as e:
            print(f"Ошибка при обработке лог-файла {item.name}: {e}")
    
    if not dry_run:
        print(f"Удалено лог-файлов старше {days_old} дней: {deleted_files}")
    else:
        print(f"Будет удалено лог-файлов старше {days_old} дней: {deleted_files}")
    
    return deleted_files

def cleanup_temp_files(dry_run=False):
    """Очистка временных файлов"""
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*~",
        "*.bak"
    ]
    
    deleted_count = 0
    for pattern in temp_patterns:
        for file_path in Path(".").glob(pattern):
            try:
                if not dry_run:
                    file_path.unlink()
                deleted_count += 1
                print(f"{'Будет удален' if dry_run else 'Удален'} временный файл: {file_path.name}")
            except Exception as e:
                print(f"Ошибка при удалении {file_path.name}: {e}")
    
    if not dry_run:
        print(f"Удалено временных файлов: {deleted_count}")
    else:
        print(f"Будет удалено временных файлов: {deleted_count}")
    
    return deleted_count

def create_test_data_directory():
    """Создание директории для тестовых данных если она не существует"""
    test_data_dir = Path("результаты/тестовые_данные")
    if not test_data_dir.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        print(f"Создана директория: {test_data_dir}")
        return True
    return False

def automatic_cleanup():
    """Автоматическая очистка после тестов"""
    print("Автоматическая очистка файлов, созданных тестами...")
    print("=" * 50)
    
    try:
        # Создаем директорию если она не существует
        create_test_data_directory()
        
        # Очищаем тестовые результаты
        files_deleted, dirs_deleted = cleanup_test_results()
        
        # Очищаем временные файлы
        temp_deleted = cleanup_temp_files()
        
        # Очищаем логи старше 7 дней
        logs_deleted = cleanup_logs(days_old=7)
        
        total_deleted = files_deleted + dirs_deleted + temp_deleted + logs_deleted
        
        print("=" * 50)
        if total_deleted > 0:
            print(f"Автоочистка завершена! Удалено {total_deleted} элементов.")
        else:
            print("Автоочистка завершена! Нет файлов для удаления.")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при автоочистке: {e}")
        return False

def manual_cleanup(dry_run=False):
    """Ручная очистка с опцией предпросмотра"""
    print(f"{'Предпросмотр' if dry_run else 'Начинаем'} очистку файлов, созданных тестами...")
    print("=" * 50)
    
    try:
        # Создаем директорию если она не существует
        created = create_test_data_directory()
        if created and dry_run:
            print("Директория будет создана при реальной очистке")
        
        # Очищаем тестовые результаты
        files_deleted, dirs_deleted = cleanup_test_results(dry_run)
        
        # Очищаем временные файлы
        temp_deleted = cleanup_temp_files(dry_run)
        
        # Очищаем логи старше 7 дней
        logs_deleted = cleanup_logs(dry_run, days_old=7)
        
        if dry_run:
            total_deleted = files_deleted + dirs_deleted + temp_deleted + logs_deleted
            print("=" * 50)
            if total_deleted > 0:
                print(f"При реальной очистке будет удалено {total_deleted} элементов.")
                print("Для выполнения очистки запустите скрипт без параметра --dry-run")
            else:
                print("При реальной очистке не будет удалено ни одного файла.")
        else:
            total_deleted = files_deleted + dirs_deleted + temp_deleted + logs_deleted
            print("=" * 50)
            if total_deleted > 0:
                print(f"Очистка завершена! Удалено {total_deleted} элементов.")
            else:
                print("Очистка завершена! Нет файлов для удаления.")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при очистке: {e}")
        return False

def main():
    """Основная функция очистки"""
    parser = argparse.ArgumentParser(description="Скрипт для очистки файлов, созданных тестами")
    parser.add_argument("--auto", action="store_true", help="Автоматическая очистка (по умолчанию)")
    parser.add_argument("--manual", action="store_true", help="Ручная очистка")
    parser.add_argument("--dry-run", action="store_true", help="Предпросмотр удаляемых файлов без реального удаления")
    parser.add_argument("--log-days", type=int, default=7, help="Удаление логов старше указанного количества дней (по умолчанию 7)")
    
    args = parser.parse_args()
    
    # Если указан --dry-run, то всегда ручной режим
    if args.dry_run:
        return manual_cleanup(dry_run=True)
    
    # По умолчанию автоматическая очистка
    if args.manual:
        return manual_cleanup(dry_run=False)
    else:
        # Для автоматической очистки используем значение по умолчанию для дней
        print("Автоматическая очистка файлов, созданных тестами...")
        print("=" * 50)
        
        try:
            # Создаем директорию если она не существует
            create_test_data_directory()
            
            # Очищаем тестовые результаты
            files_deleted, dirs_deleted = cleanup_test_results()
            
            # Очищаем временные файлы
            temp_deleted = cleanup_temp_files()
            
            # Очищаем логи старше 7 дней
            logs_deleted = cleanup_logs(days_old=args.log_days)
            
            total_deleted = files_deleted + dirs_deleted + temp_deleted + logs_deleted
            
            print("=" * 50)
            if total_deleted > 0:
                print(f"Автоочистка завершена! Удалено {total_deleted} элементов.")
            else:
                print("Автоочистка завершена! Нет файлов для удаления.")
            
            return True
            
        except Exception as e:
            print(f"Ошибка при автоочистке: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)