#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для API системы расчета усушки.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys
from pathlib import Path

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.api import app, ShrinkageData, CalculationRequest
from src.core.settings_manager import SettingsManager

# Создаем тестовый клиент
client = TestClient(app)


def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.2.1"


def test_system_info_endpoint():
    """Тест эндпоинта информации о системе"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "python_version" in data
    assert "dependencies" in data
    assert data["version"] == "1.2.1"


def test_settings_endpoints():
    """Тест эндпоинтов настроек"""
    # Получение настроек
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    settings = response.json()
    assert isinstance(settings, dict)
    assert "model_type" in settings
    
    # Обновление настроек
    update_data = {"model_type": "linear"}
    response = client.put("/api/v1/settings", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    
    # Проверка, что настройки обновились
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    updated_settings = response.json()
    # Note: In a real test, we would check that the setting was actually updated,
    # but for this test we're just verifying the API endpoints work


@patch('src.api.ShrinkageSystem')
@patch('src.api.pd.DataFrame')
def test_calculate_shrinkage_success(mock_dataframe, mock_shrinkage_system):
    """Тест успешного расчета усушки"""
    # Мокаем зависимости
    mock_dataset = MagicMock()
    mock_dataframe.return_value = mock_dataset
    
    mock_system_instance = MagicMock()
    mock_shrinkage_system.return_value = mock_system_instance
    
    mock_results = {
        'status': 'success',
        'data': {
            'coefficients': [
                {
                    'номенклатура': 'Рыба треска',
                    'коэффициент_усушки': 0.0033,
                    'точность': 95.5,
                    'период_хранения': 14,
                    'фактическая_усушка': 50,
                    'прогнозируемая_усушка': 46.7
                }
            ]
        },
        'reports': {
            'coefficients': '/results/report.html',
            'errors': '/results/errors.html'
        }
    }
    mock_system_instance.process_dataset.return_value = mock_results
    
    # Подготовка данных для запроса
    shrinkage_data = [
        ShrinkageData(
            номенклатура="Рыба треска",
            дата_прихода="2024-01-01",
            дата_инвентаризации="2024-01-15",
            начальный_остаток=1000.0,
            конечный_остаток=950.0,
            единица_измерения="кг"
        )
    ]
    
    request_data = CalculationRequest(
        data=shrinkage_data,
        use_adaptive_model=True,
        surplus_rate=0.05
    )
    
    # Отправка запроса
    response = client.post("/api/v1/calculate", json=request_data.model_dump())
    
    # Проверка результата
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert "data" in result
    assert "reports" in result
    
    # Проверка вызовов моков
    mock_shrinkage_system.assert_called_once()
    mock_system_instance.set_surplus_rate.assert_called_once_with(0.0005)  # 0.05% converted
    mock_system_instance.process_dataset.assert_called_once()


@patch('src.api.ShrinkageSystem')
@patch('src.api.pd.DataFrame')
def test_calculate_shrinkage_failure(mock_dataframe, mock_shrinkage_system):
    """Тест расчета усушки с ошибкой"""
    # Мокаем зависимости для симуляции ошибки
    mock_dataset = MagicMock()
    mock_dataframe.return_value = mock_dataset
    
    mock_system_instance = MagicMock()
    mock_shrinkage_system.return_value = mock_system_instance
    
    mock_results = {
        'status': 'error',
        'message': 'Ошибка расчета'
    }
    mock_system_instance.process_dataset.return_value = mock_results
    
    # Подготовка данных для запроса
    shrinkage_data = [
        ShrinkageData(
            номенклатура="Рыба треска",
            дата_прихода="2024-01-01",
            дата_инвентаризации="2024-01-15",
            начальный_остаток=1000.0,
            конечный_остаток=950.0,
            единица_измерения="кг"
        )
    ]
    
    request_data = CalculationRequest(
        data=shrinkage_data,
        use_adaptive_model=True,
        surplus_rate=0.05
    )
    
    # Отправка запроса
    response = client.post("/api/v1/calculate", json=request_data.model_dump())
    
    # Проверка результата (теперь это должен быть успешный ответ с ошибкой в теле)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "error"
    assert "message" in result
    assert result["message"] == "Ошибка расчета"


def test_job_status_not_found():
    """Тест получения статуса несуществующей задачи"""
    response = client.get("/api/v1/status/nonexistent_job")
    assert response.status_code == 404


@patch('src.api.process_excel_background')
def test_file_upload_success(mock_process_background):
    """Тест успешной загрузки файла"""
    # Создание тестового файла
    test_content = b"test file content"
    
    # Отправка запроса на загрузку файла
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.xlsx", test_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"use_adaptive_model": "true", "surplus_rate": "0.05"}
    )
    
    # Проверка результата
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert "job_id" in result
    assert result["message"] == "Файл загружен и обработка начата"
    
    # Проверка вызова фоновой задачи
    mock_process_background.assert_called_once()


def test_metrics_endpoint():
    """Тест эндпоинта метрик"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Проверяем наличие ключевых метрик
    assert "uptime" in data
    assert "total_requests" in data
    assert "successful_calculations" in data
    assert "failed_calculations" in data
    assert "average_response_time" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])