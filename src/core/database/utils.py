#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для работы с базой данных.

Этот файл предоставляет вспомогательные функции для инициализации,
обслуживания и работы с базой данных.
"""

import os
import shutil
from datetime import datetime
from sqlalchemy import text
from src.logger_config import log
from src.core.database.database import get_db_session, get_database_url
from src.core.database.models import Base

def initialize_database():
    """
    Инициализирует базу данных, создавая все таблицы.
    """
    try:
        from src.core.database.database import init_database
        engine = init_database()
        log.success("База данных успешно инициализирована")
        return engine
    except Exception as e:
        log.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def create_database_backup(backup_path: str = None) -> str:
    """
    Создает резервную копию базы данных.
    
    Args:
        backup_path (str): Путь для сохранения резервной копии
        
    Returns:
        str: Путь к созданной резервной копии
    """
    try:
        # Получаем путь к текущей базе данных
        db_url = get_database_url()
        
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            
            # Создаем директорию для резервных копий, если она не существует
            if backup_path is None:
                backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
            else:
                backup_dir = backup_path
                
            os.makedirs(backup_dir, exist_ok=True)
            
            # Создаем имя файла резервной копии с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_filename = os.path.basename(db_path)
            backup_filename = f"{db_filename}_{timestamp}.bak"
            backup_file_path = os.path.join(backup_dir, backup_filename)
            
            # Копируем файл базы данных
            shutil.copy2(db_path, backup_file_path)
            log.info(f"Резервная копия базы данных создана: {backup_file_path}")
            
            return backup_file_path
        elif db_url.startswith('postgresql://'):
            log.warning("Резервное копирование для PostgreSQL должно выполняться через pg_dump")
            return None
        else:
            log.warning("Резервное копирование поддерживается только для SQLite")
            return None
    except Exception as e:
        log.error(f"Ошибка при создании резервной копии базы данных: {e}")
        raise

def restore_database_from_backup(backup_file_path: str) -> bool:
    """
    Восстанавливает базу данных из резервной копии.
    
    Args:
        backup_file_path (str): Путь к файлу резервной копии
        
    Returns:
        bool: True, если восстановление успешно
    """
    try:
        # Проверяем существование файла резервной копии
        if not os.path.exists(backup_file_path):
            log.error(f"Файл резервной копии не найден: {backup_file_path}")
            return False
            
        # Получаем путь к текущей базе данных
        db_url = get_database_url()
        
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            
            # Закрываем все соединения с базой данных
            # Это важно для SQLite, так как он блокирует файл
            # В реальном приложении здесь нужно будет корректно закрыть все сессии
            
            # Копируем файл резервной копии на место базы данных
            shutil.copy2(backup_file_path, db_path)
            log.success(f"База данных восстановлена из резервной копии: {backup_file_path}")
            
            return True
        elif db_url.startswith('postgresql://'):
            log.warning("Восстановление для PostgreSQL должно выполняться через pg_restore")
            return False
        else:
            log.warning("Восстановление поддерживается только для SQLite")
            return False
    except Exception as e:
        log.error(f"Ошибка при восстановлении базы данных из резервной копии: {e}")
        raise

def get_database_size() -> int:
    """
    Получает размер файла базы данных.
    
    Returns:
        int: Размер файла базы данных в байтах
    """
    try:
        db_url = get_database_url()
        
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                return size
            else:
                return 0
        elif db_url.startswith('postgresql://'):
            # Для PostgreSQL получаем размер через SQL запрос
            Session = get_db_session()
            session = Session()
            
            try:
                result = session.execute(text(
                    "SELECT pg_database_size(current_database())"
                ))
                size = result.scalar()
                session.close()
                return size if size else 0
            except Exception as e:
                session.close()
                log.error(f"Ошибка при получении размера PostgreSQL базы данных: {e}")
                return 0
        else:
            log.warning("Получение размера поддерживается только для SQLite и PostgreSQL")
            return 0
    except Exception as e:
        log.error(f"Ошибка при получении размера базы данных: {e}")
        return 0

def get_table_row_counts() -> dict:
    """
    Получает количество строк в каждой таблице базы данных.
    
    Returns:
        dict: Словарь с количеством строк в каждой таблице
    """
    try:
        Session = get_db_session()
        session = Session()
        
        # Получаем список всех таблиц
        table_names = Base.metadata.tables.keys()
        row_counts = {}
        
        # Для каждой таблицы получаем количество строк
        for table_name in table_names:
            try:
                # Используем сырые SQL запросы для подсчета строк
                if get_database_url().startswith('postgresql://'):
                    result = session.execute(text(f"SELECT COUNT(*) FROM \"{table_name}\""))
                else:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                row_counts[table_name] = count
            except Exception as e:
                log.warning(f"Не удалось получить количество строк для таблицы {table_name}: {e}")
                row_counts[table_name] = -1
        
        session.close()
        return row_counts
    except Exception as e:
        log.error(f"Ошибка при получении количества строк в таблицах: {e}")
        raise

def cleanup_old_data(days_old: int = 30) -> int:
    """
    Удаляет старые данные из базы данных.
    
    Args:
        days_old (int): Количество дней, после которых данные считаются старыми
        
    Returns:
        int: Количество удаленных записей
    """
    try:
        log.info(f"Начало очистки данных старше {days_old} дней")
        # Пока не реализуем, так как это требует более сложной логики
        # и может повлиять на целостность данных
        log.info("Очистка старых данных временно не реализована")
        return 0
    except Exception as e:
        log.error(f"Ошибка при очистке старых данных: {e}")
        raise

def vacuum_database() -> bool:
    """
    Выполняет оптимизацию базы данных (VACUUM для SQLite, REINDEX для PostgreSQL).
    
    Returns:
        bool: True, если оптимизация успешна
    """
    try:
        db_url = get_database_url()
        
        if db_url.startswith('sqlite:///'):
            Session = get_db_session()
            session = Session()
            
            # Выполняем VACUUM для SQLite
            session.execute(text("VACUUM"))
            session.commit()
            session.close()
            
            log.info("База данных оптимизирована (VACUUM)")
            return True
        elif db_url.startswith('postgresql://'):
            Session = get_db_session()
            session = Session()
            
            # Для PostgreSQL выполняем REINDEX и ANALYZE
            session.execute(text("REINDEX DATABASE CURRENT_DATABASE()"))
            session.execute(text("ANALYZE"))
            session.commit()
            session.close()
            
            log.info("База данных оптимизирована (REINDEX и ANALYZE)")
            return True
        else:
            log.warning("Оптимизация поддерживается только для SQLite и PostgreSQL")
            return False
    except Exception as e:
        log.error(f"Ошибка при оптимизации базы данных: {e}")
        raise

# Функции для тестирования подключения к базе данных
def test_database_connection() -> bool:
    """
    Тестирует подключение к базе данных.
    
    Returns:
        bool: True, если подключение успешно
    """
    try:
        Session = get_db_session()
        session = Session()
        
        # Выполняем простой запрос для проверки подключения
        session.execute(text("SELECT 1"))
        session.close()
        
        log.info("Подключение к базе данных успешно протестировано")
        return True
    except Exception as e:
        log.error(f"Ошибка при тестировании подключения к базе данных: {e}")
        return False

def get_database_info() -> dict:
    """
    Получает информацию о базе данных.
    
    Returns:
        dict: Словарь с информацией о базе данных
    """
    try:
        db_url = get_database_url()
        size = get_database_size()
        table_counts = get_table_row_counts()
        
        # Определяем тип базы данных
        if db_url.startswith('sqlite:///'):
            db_type = 'SQLite'
        elif db_url.startswith('postgresql://'):
            db_type = 'PostgreSQL'
        else:
            db_type = 'Unknown'
        
        info = {
            'database_url': db_url,
            'database_type': db_type,
            'size_bytes': size,
            'size_mb': round(size / (1024 * 1024), 2) if size > 0 else 0,
            'tables': table_counts,
            'total_rows': sum(count for count in table_counts.values() if count > 0)
        }
        
        return info
    except Exception as e:
        log.error(f"Ошибка при получении информации о базе данных: {e}")
        raise