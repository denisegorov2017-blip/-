#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль конфигурации и подключения к базе данных.

Этот файл предоставляет функциональность для инициализации и подключения
к базе данных PostgreSQL с использованием SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from src.logger_config import log

# Импортируем модели
from src.core.database.models import Base

# Получаем путь к директории проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(PROJECT_ROOT, 'shrinkage_database.db')

def get_database_url():
    """
    Получает URL для подключения к базе данных.
    
    Returns:
        str: URL для подключения к базе данных
    """
    # Для начала используем SQLite для упрощения развертывания
    # В будущем можно переключиться на PostgreSQL
    return f"sqlite:///{DB_PATH}"

def create_database_engine():
    """
    Создает движок базы данных.
    
    Returns:
        Engine: Движок SQLAlchemy для работы с базой данных
    """
    try:
        database_url = get_database_url()
        log.info(f"Создание подключения к базе данных: {database_url}")
        
        # Для SQLite используем StaticPool для избежания проблем с блокировками
        if database_url.startswith('sqlite'):
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={'check_same_thread': False},
                echo=False  # Установите True для отладки SQL запросов
            )
        else:
            # Для PostgreSQL
            engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                echo=False  # Установите True для отладки SQL запросов
            )
        
        return engine
    except Exception as e:
        log.error(f"Ошибка при создании подключения к базе данных: {e}")
        raise

def init_database():
    """
    Инициализирует базу данных, создавая все таблицы.
    """
    try:
        engine = create_database_engine()
        log.info("Инициализация базы данных...")
        
        # Создаем все таблицы
        Base.metadata.create_all(engine)
        log.success("База данных успешно инициализирована")
        
        return engine
    except Exception as e:
        log.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def get_session():
    """
    Создает и возвращает сессию базы данных.
    
    Returns:
        Session: Сессия SQLAlchemy для работы с базой данных
    """
    try:
        engine = create_database_engine()
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        return Session
    except Exception as e:
        log.error(f"Ошибка при создании сессии базы данных: {e}")
        raise

# Глобальный движок и сессия для использования в приложении
engine = None
Session = None

def get_db_engine():
    """
    Получает глобальный движок базы данных.
    
    Returns:
        Engine: Глобальный движок базы данных
    """
    global engine
    if engine is None:
        engine = create_database_engine()
    return engine

def get_db_session():
    """
    Получает глобальную сессию базы данных.
    
    Returns:
        Session: Глобальная сессия базы данных
    """
    global Session
    if Session is None:
        engine = get_db_engine()
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
    return Session

# Инициализируем базу данных при импорте модуля
try:
    engine = create_database_engine()
    log.info("Модуль базы данных успешно загружен")
except Exception as e:
    log.error(f"Ошибка при загрузке модуля базы данных: {e}")