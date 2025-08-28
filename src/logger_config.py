#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Централизованная конфигурация логгера Loguru.
"""

import sys
from loguru import logger

# Удаляем стандартный обработчик, чтобы избежать дублирования
logger.remove()

# Настраиваем логирование в консоль с уровнем INFO
logger.add(
    sys.stderr, 
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Настраиваем логирование в файл с уровнем DEBUG, ротацией и сжатием
logger.add(
    "logs/project_{time:YYYY-MM-DD}.log", 
    rotation="10 MB", 
    compression="zip", 
    level="DEBUG",
    encoding="utf-8"
)

# Экспортируем настроенный логгер для использования в других модулях
log = logger
