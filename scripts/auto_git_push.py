#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для автоматической отправки изменений в Git репозиторий
Автоматически добавляет, коммитит и отправляет изменения в удаленный репозиторий
"""

import subprocess
import sys
import os
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/git_auto_push.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_git_command(command):
    """
    Выполняет Git команду и возвращает результат
    
    Args:
        command (str): Команда для выполнения
        
    Returns:
        tuple: (stdout, stderr, returncode)
    """
    try:
        logger.info(f"Выполнение команды: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(),
            encoding='utf-8'
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды {command}: {e}")
        return "", str(e), 1

def check_git_status():
    """
    Проверяет статус Git репозитория
    
    Returns:
        bool: True если есть изменения для отправки, False если нет
    """
    stdout, stderr, returncode = run_git_command("git status --porcelain")
    
    if returncode != 0:
        logger.error(f"Ошибка при проверке статуса Git: {stderr}")
        return False
    
    # Если есть вывод, значит есть изменения
    has_changes = bool(stdout.strip())
    if has_changes:
        logger.info("Обнаружены изменения для отправки")
        logger.debug(f"Изменения:\n{stdout}")
    else:
        logger.info("Нет изменений для отправки")
    
    return has_changes

def git_add_all():
    """
    Добавляет все изменения в индекс Git
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    stdout, stderr, returncode = run_git_command("git add .")
    
    if returncode != 0:
        logger.error(f"Ошибка при добавлении файлов в индекс: {stderr}")
        return False
    
    logger.info("Все изменения добавлены в индекс")
    return True

def analyze_changes():
    """
    Анализирует изменения для формирования осмысленного сообщения коммита
    
    Returns:
        str: Тип изменений (feat, fix, docs, chore и т.д.)
    """
    stdout, stderr, returncode = run_git_command("git diff --cached --name-only")
    
    if returncode != 0:
        logger.warning("Не удалось проанализировать изменения")
        return "chore"
    
    changed_files = stdout.strip().split('\n') if stdout.strip() else []
    
    # Определяем тип изменений на основе расширений файлов и путей
    has_py_files = any(f.endswith('.py') for f in changed_files)
    has_doc_files = any(f.endswith(('.md', '.txt', '.rst')) for f in changed_files)
    has_src_files = any('src/' in f or 'core/' in f for f in changed_files)
    has_test_files = any('test' in f.lower() for f in changed_files)
    
    if has_src_files and has_py_files:
        return "feat"  # Новая функциональность в коде
    elif has_test_files:
        return "test"  # Изменения в тестах
    elif has_doc_files:
        return "docs"  # Изменения в документации
    else:
        return "chore"  # Технические изменения

def git_commit(message=None):
    """
    Создает коммит с изменениями
    
    Args:
        message (str): Сообщение коммита. Если не указано, генерируется автоматически
        
    Returns:
        bool: True если успешно, False если ошибка
    """
    if not message:
        # Анализируем изменения для определения типа коммита
        commit_type = analyze_changes()
        
        # Генерируем сообщение коммита по стандартам Conventional Commits на русском
        if commit_type == "feat":
            message = "feat: добавление новой функциональности"
        elif commit_type == "fix":
            message = "fix: исправление ошибок"
        elif commit_type == "docs":
            message = "docs: обновление документации"
        elif commit_type == "test":
            message = "test: изменения в тестах"
        elif commit_type == "style":
            message = "style: форматирование кода"
        elif commit_type == "refactor":
            message = "refactor: рефакторинг кода"
        else:
            # Для chore и других типов
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"chore: автоматический коммит от {timestamp}"
    
    # Экранируем кавычки в сообщении
    message = message.replace('"', '\\"')
    command = f'git commit -m "{message}"'
    
    stdout, stderr, returncode = run_git_command(command)
    
    if returncode != 0:
        if "nothing to commit" in stderr or "nothing added to commit" in stderr:
            logger.info("Нет изменений для коммита")
            return True
        else:
            logger.error(f"Ошибка при создании коммита: {stderr}")
            return False
    
    logger.info(f"Создан коммит: {message}")
    return True

def git_push():
    """
    Отправляет изменения в удаленный репозиторий
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    stdout, stderr, returncode = run_git_command("git push origin main")
    
    if returncode != 0:
        logger.error(f"Ошибка при отправке изменений: {stderr}")
        return False
    
    logger.info("Изменения успешно отправлены в удаленный репозиторий")
    return True

def auto_git_push(commit_message=None):
    """
    Основная функция для автоматической отправки изменений в Git
    
    Args:
        commit_message (str): Сообщение для коммита (опционально)
        
    Returns:
        bool: True если успешно, False если ошибка
    """
    try:
        logger.info("Начало автоматической отправки изменений в Git")
        
        # Проверяем статус репозитория
        if not check_git_status():
            logger.info("Нет изменений для отправки. Завершение работы.")
            return True
        
        # Добавляем все изменения
        if not git_add_all():
            logger.error("Не удалось добавить изменения в индекс")
            return False
        
        # Создаем коммит
        if not git_commit(commit_message):
            logger.error("Не удалось создать коммит")
            return False
        
        # Отправляем изменения
        if not git_push():
            logger.error("Не удалось отправить изменения в удаленный репозиторий")
            return False
        
        logger.info("Автоматическая отправка изменений успешно завершена")
        return True
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при автоматической отправке: {e}")
        return False

if __name__ == "__main__":
    # Если скрипт запущен напрямую, выполняем автоматическую отправку
    commit_msg = None
    if len(sys.argv) > 1:
        commit_msg = " ".join(sys.argv[1:])
    
    success = auto_git_push(commit_msg)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)