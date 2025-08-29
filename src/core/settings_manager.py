#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления настройками системы расчета усушки.

Этот модуль предоставляет централизованное управление настройками для всех компонентов системы,
включая графические интерфейсы, ядро расчетов и интеграции.
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
import shutil
from datetime import datetime

# Add the src directory to the path so we can import modules
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.config import DEFAULT_CONFIG, CONFIG_VALIDATION_RULES
from src.logger_config import log


class SettingsValidationError(Exception):
    """Исключение для ошибок валидации настроек"""
    pass


class SettingsManager:
    """
    Класс для управления настройками системы.
    
    Предоставляет функции для загрузки, сохранения, валидации и управления настройками системы.
    """
    
    def __init__(self, settings_file: str = "результаты/system_settings.json"):
        """
        Инициализирует менеджер настроек.
        
        Args:
            settings_file (str): Путь к файлу настроек.
        """
        self.settings_file = settings_file
        self.settings = {}
        self.default_settings = DEFAULT_CONFIG.copy()
        
        # Загружаем настройки из файла или используем значения по умолчанию
        self.load_settings()
        
        log.info("SettingsManager инициализирован")
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Загружает настройки из файла.
        
        Returns:
            Dict[str, Any]: Словарь с настройками системы.
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Объединяем сохраненные настройки с настройками по умолчанию
                    self.settings = {**self.default_settings, **saved_settings}
                    # Валидируем загруженные настройки
                    self._validate_settings(self.settings)
            else:
                # Если файл настроек не существует, используем значения по умолчанию
                self.settings = self.default_settings.copy()
                # Создаем директорию если она не существует
                Path(self.settings_file).parent.mkdir(parents=True, exist_ok=True)
                self.save_settings()
                
            log.info(f"Настройки загружены из {self.settings_file}")
            return self.settings
        except SettingsValidationError as e:
            log.error(f"Ошибка валидации настроек: {e}")
            # В случае ошибки валидации используем настройки по умолчанию
            self.settings = self.default_settings.copy()
            return self.settings
        except Exception as e:
            log.error(f"Ошибка при загрузке настроек: {e}")
            # В случае ошибки используем настройки по умолчанию
            self.settings = self.default_settings.copy()
            return self.settings
    
    def save_settings(self) -> bool:
        """
        Сохраняет настройки в файл.
        
        Returns:
            bool: True если сохранение прошло успешно, False в противном случае.
        """
        try:
            # Валидируем настройки перед сохранением
            self._validate_settings(self.settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2, default=str)
            log.info(f"Настройки сохранены в {self.settings_file}")
            return True
        except SettingsValidationError as e:
            log.error(f"Ошибка валидации настроек при сохранении: {e}")
            return False
        except Exception as e:
            log.error(f"Ошибка при сохранении настроек: {e}")
            return False
    
    def _validate_settings(self, settings: Dict[str, Any]) -> None:
        """
        Валидирует настройки согласно правилам валидации.
        
        Args:
            settings (Dict[str, Any]): Словарь с настройками для валидации.
            
        Raises:
            SettingsValidationError: Если настройки не прошли валидацию.
        """
        errors = []
        
        for key, rules in CONFIG_VALIDATION_RULES.items():
            value = settings.get(key)
            
            # Проверка обязательных полей
            if rules.get('required', False) and value is None:
                errors.append(f"Обязательное поле '{key}' отсутствует")
                continue
            
            # Если значение None и не обязательное, пропускаем
            if value is None and not rules.get('required', False):
                continue
            
            # Проверка типа
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Поле '{key}' должно быть типа {expected_type.__name__}, получено {type(value).__name__}")
                continue
            
            # Проверка допустимых значений
            allowed_values = rules.get('allowed_values')
            if allowed_values and value not in allowed_values:
                errors.append(f"Поле '{key}' имеет недопустимое значение '{value}'. Допустимые значения: {allowed_values}")
            
            # Проверка минимального значения
            min_value = rules.get('min')
            if min_value is not None and isinstance(value, (int, float)) and value < min_value:
                errors.append(f"Поле '{key}' должно быть не меньше {min_value}, получено {value}")
            
            # Проверка максимального значения
            max_value = rules.get('max')
            if max_value is not None and isinstance(value, (int, float)) and value > max_value:
                errors.append(f"Поле '{key}' должно быть не больше {max_value}, получено {value}")
        
        if errors:
            raise SettingsValidationError("Ошибки валидации настроек:\n" + "\n".join(errors))
    
    def get_setting(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Получает значение настройки по ключу.
        
        Args:
            key (str): Ключ настройки.
            default (Optional[Any]): Значение по умолчанию, если ключ не найден.
            
        Returns:
            Any: Значение настройки или значение по умолчанию.
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Устанавливает значение настройки с валидацией.
        
        Args:
            key (str): Ключ настройки.
            value (Any): Значение настройки.
            
        Returns:
            bool: True если установка прошла успешно, False в противном случае.
        """
        try:
            # Создаем временную копию настроек для валидации
            temp_settings = self.settings.copy()
            temp_settings[key] = value
            
            # Валидируем изменения
            self._validate_settings(temp_settings)
            
            # Если валидация прошла успешно, применяем изменения
            self.settings[key] = value
            return True
        except SettingsValidationError as e:
            log.error(f"Ошибка валидации при установке настройки '{key}': {e}")
            return False
        except Exception as e:
            log.error(f"Ошибка при установке настройки '{key}': {e}")
            return False
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """
        Обновляет несколько настроек одновременно с валидацией.
        
        Args:
            new_settings (Dict[str, Any]): Словарь с новыми настройками.
            
        Returns:
            bool: True если обновление прошло успешно, False в противном случае.
        """
        try:
            # Создаем временную копию настроек для валидации
            temp_settings = self.settings.copy()
            temp_settings.update(new_settings)
            
            # Валидируем изменения
            self._validate_settings(temp_settings)
            
            # Если валидация прошла успешно, применяем изменения
            self.settings.update(new_settings)
            return True
        except SettingsValidationError as e:
            log.error(f"Ошибка валидации при обновлении настроек: {e}")
            return False
        except Exception as e:
            log.error(f"Ошибка при обновлении настроек: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Сбрасывает все настройки к значениям по умолчанию.
        
        Returns:
            bool: True если сброс прошел успешно, False в противном случае.
        """
        try:
            self.settings = self.default_settings.copy()
            self.save_settings()
            log.info("Настройки сброшены к значениям по умолчанию")
            return True
        except Exception as e:
            log.error(f"Ошибка при сбросе настроек к значениям по умолчанию: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Возвращает все настройки системы.
        
        Returns:
            Dict[str, Any]: Словарь со всеми настройками.
        """
        return self.settings.copy()
    
    def backup_settings(self, backup_file: Optional[str] = None) -> bool:
        """
        Создает резервную копию файла настроек.
        
        Args:
            backup_file (Optional[str]): Путь к файлу резервной копии.
            
        Returns:
            bool: True если резервное копирование прошло успешно, False в противном случае.
        """
        try:
            if backup_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{self.settings_file}.backup_{timestamp}"
            
            # Убедимся, что директория для резервной копии существует
            Path(backup_file).parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(self.settings_file, backup_file)
            
            log.info(f"Резервная копия настроек создана: {backup_file}")
            return True
        except Exception as e:
            log.error(f"Ошибка при создании резервной копии настроек: {e}")
            return False
    
    def restore_settings_from_backup(self, backup_file: str) -> bool:
        """
        Восстанавливает настройки из резервной копии.
        
        Args:
            backup_file (str): Путь к файлу резервной копии.
            
        Returns:
            bool: True если восстановление прошло успешно, False в противном случае.
        """
        try:
            if not os.path.exists(backup_file):
                log.error(f"Файл резервной копии не найден: {backup_file}")
                return False
            
            # Создаем резервную копию текущих настроек перед восстановлением
            self.backup_settings()
            
            # Восстанавливаем настройки из резервной копии
            shutil.copy2(backup_file, self.settings_file)
            
            # Перезагружаем настройки
            self.load_settings()
            
            log.info(f"Настройки восстановлены из резервной копии: {backup_file}")
            return True
        except Exception as e:
            log.error(f"Ошибка при восстановлении настроек из резервной копии: {e}")
            return False


# Глобальный экземпляр менеджера настроек для использования в других модулях
settings_manager = SettingsManager()


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр менеджера настроек
    sm = SettingsManager()
    
    # Получаем настройки
    print("Текущие настройки:")
    for key, value in sm.get_all_settings().items():
        print(f"  {key}: {value}")
    
    # Изменяем настройку
    success = sm.set_setting('min_accuracy', 75.0)
    if success:
        print(f"\nИзмененная настройка min_accuracy: {sm.get_setting('min_accuracy')}")
        
        # Сохраняем настройки
        if sm.save_settings():
            print("\nНастройки сохранены")
        else:
            print("\nОшибка при сохранении настроек")
    else:
        print("\nОшибка при изменении настройки")