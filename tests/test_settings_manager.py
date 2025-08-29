#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для менеджера настроек системы расчета усушки.
"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path

# Добавляем путь к src директории
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.settings_manager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    """Тесты для SettingsManager"""

    def setUp(self):
        """Создаем временный файл для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.test_dir, "test_settings.json")
        self.sm = SettingsManager(self.settings_file)

    def tearDown(self):
        """Удаляем временные файлы"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Тест инициализации менеджера настроек"""
        # Проверяем, что настройки загружены
        self.assertIsInstance(self.sm.settings, dict)
        self.assertGreater(len(self.sm.settings), 0)

    def test_get_setting(self):
        """Тест получения настройки"""
        # Проверяем получение существующей настройки
        model_type = self.sm.get_setting('model_type')
        self.assertEqual(model_type, 'exponential')

        # Проверяем получение несуществующей настройки с значением по умолчанию
        default_value = self.sm.get_setting('nonexistent_setting', 'default')
        self.assertEqual(default_value, 'default')

    def test_set_setting(self):
        """Тест установки настройки"""
        # Устанавливаем новое значение
        self.sm.set_setting('test_key', 'test_value')
        
        # Проверяем, что значение установлено
        self.assertEqual(self.sm.get_setting('test_key'), 'test_value')

    def test_update_settings(self):
        """Тест обновления нескольких настроек"""
        # Создаем словарь с новыми настройками
        new_settings = {
            'model_type': 'linear',
            'min_accuracy': 75.0,
            'test_key': 'test_value'
        }
        
        # Обновляем настройки
        self.sm.update_settings(new_settings)
        
        # Проверяем, что настройки обновлены
        self.assertEqual(self.sm.get_setting('model_type'), 'linear')
        self.assertEqual(self.sm.get_setting('min_accuracy'), 75.0)
        self.assertEqual(self.sm.get_setting('test_key'), 'test_value')

    def test_save_and_load_settings(self):
        """Тест сохранения и загрузки настроек"""
        # Изменяем настройки
        self.sm.set_setting('test_key', 'test_value')
        
        # Сохраняем настройки
        self.assertTrue(self.sm.save_settings())
        
        # Создаем новый экземпляр менеджера настроек
        new_sm = SettingsManager(self.settings_file)
        
        # Проверяем, что настройки загружены
        self.assertEqual(new_sm.get_setting('test_key'), 'test_value')

    def test_reset_to_defaults(self):
        """Тест сброса настроек к значениям по умолчанию"""
        # Изменяем настройки
        self.sm.set_setting('model_type', 'linear')
        self.sm.set_setting('min_accuracy', 75.0)
        
        # Сохраняем настройки
        self.sm.save_settings()
        
        # Сбрасываем к значениям по умолчанию
        self.sm.reset_to_defaults()
        
        # Проверяем, что настройки сброшены
        self.assertEqual(self.sm.get_setting('model_type'), 'exponential')
        self.assertEqual(self.sm.get_setting('min_accuracy'), 50.0)

    def test_backup_settings(self):
        """Тест создания резервной копии настроек"""
        # Изменяем настройки
        self.sm.set_setting('test_key', 'test_value')
        
        # Сохраняем настройки перед созданием резервной копии
        self.sm.save_settings()
        
        # Создаем резервную копию
        backup_file = self.settings_file + ".backup"
        self.assertTrue(self.sm.backup_settings(backup_file))
        
        # Проверяем, что файл резервной копии существует
        self.assertTrue(os.path.exists(backup_file))
        
        # Проверяем содержимое резервной копии
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        self.assertEqual(backup_data['test_key'], 'test_value')
        
        # Удаляем файл резервной копии
        os.remove(backup_file)


if __name__ == '__main__':
    unittest.main()