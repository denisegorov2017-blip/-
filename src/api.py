#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API для системы расчета усушки.

Этот модуль предоставляет веб-API для интеграции системы расчета усушки
с другими приложениями и сервисами.
"""

import os
import sys
import uuid
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.core.shrinkage_system import ShrinkageSystem
from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
from src.core.improved_json_parser import parse_from_json
from src.core.settings_manager import SettingsManager
from src.logger_config import log

# Инициализация FastAPI приложения
app = FastAPI(
    title="Система Расчета Усушки API",
    description="REST API для расчета коэффициентов нелинейной усушки",
    version="1.2.1",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище для фоновых задач
jobs = {}

# Модели данных
class ShrinkageData(BaseModel):
    """Модель данных для расчета усушки"""
    номенклатура: str = Field(..., example="Рыба треска")
    дата_прихода: str = Field(..., example="2024-01-01")
    дата_инвентаризации: str = Field(..., example="2024-01-15")
    начальный_остаток: float = Field(..., example=1000.0)
    конечный_остаток: float = Field(..., example=950.0)
    единица_измерения: str = Field(..., example="кг")


class CalculationRequest(BaseModel):
    """Запрос для расчета усушки"""
    data: List[ShrinkageData]
    use_adaptive_model: bool = False
    surplus_rate: float = 0.0


class CoefficientResult(BaseModel):
    """Результат расчета коэффициента усушки"""
    номенклатура: str
    коэффициент_усушки: float
    точность: float
    период_хранения: int
    фактическая_усушка: float
    прогнозируемая_усушка: float


class CalculationSummary(BaseModel):
    """Сводка по расчету"""
    total_positions: int
    avg_accuracy: float
    error_count: int


class CalculationResponse(BaseModel):
    """Ответ на запрос расчета"""
    status: str
    data: Optional[Dict] = None
    reports: Optional[Dict] = None
    message: Optional[str] = None


class JobStatus(BaseModel):
    """Статус фоновой задачи"""
    status: str  # pending, processing, completed, failed
    progress: int = 0  # 0-100
    result: Optional[Dict] = None
    error: Optional[str] = None


class SettingsUpdate(BaseModel):
    """Модель для обновления настроек"""
    model_type: Optional[str] = None
    default_period: Optional[int] = None
    min_accuracy: Optional[float] = None
    use_adaptive_model: Optional[bool] = None
    # Добавьте другие настройки по необходимости


# Вспомогательные функции
def process_excel_background(file_path: str, job_id: str, use_adaptive: bool = False, surplus_rate: float = 0.0):
    """
    Фоновая обработка Excel файла.
    
    Args:
        file_path (str): Путь к Excel файлу
        job_id (str): Идентификатор задачи
        use_adaptive (bool): Использовать адаптивную модель
        surplus_rate (float): Процент излишка
    """
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        
        # Получаем настройки
        settings_manager = SettingsManager()
        output_dir = settings_manager.get_setting('output_dir', 'результаты')
        
        # Создаем директорию для результатов если она не существует
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Этап 1: Конвертация Excel в JSON (30%)
        jobs[job_id]["progress"] = 30
        json_path = os.path.join(output_dir, f"{Path(file_path).stem}.json")
        
        preserver = ExcelHierarchyPreserver(file_path)
        preserver.to_json(json_path)
        
        # Этап 2: Парсинг JSON (60%)
        jobs[job_id]["progress"] = 60
        dataset = parse_from_json(json_path)
        
        if dataset.empty:
            raise ValueError("В файле не найдено данных для расчета")
        
        # Этап 3: Расчет коэффициентов (90%)
        jobs[job_id]["progress"] = 90
        system = ShrinkageSystem()
        
        # Устанавливаем процент излишка если указан
        if surplus_rate > 0:
            system.set_surplus_rate(surplus_rate / 100.0)
        
        # Обрабатываем набор данных
        results = system.process_dataset(
            dataset=dataset,
            source_filename=os.path.basename(file_path),
            use_adaptive=use_adaptive
        )
        
        if results.get('status') == 'success':
            # Завершено (100%)
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["result"] = {
                "coefficients_report": results.get('reports', {}).get('coefficients', ''),
                "errors_report": results.get('reports', {}).get('errors', '')
            }
        else:
            error_msg = results.get('message', 'Неизвестная ошибка')
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = error_msg
            
    except Exception as e:
        log.exception(f"Ошибка при фоновой обработке файла: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
    finally:
        # Удаляем временный файл если он существует
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            log.warning(f"Не удалось удалить временный файл {file_path}: {e}")


# Эндпоинты API

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Система Расчета Усушки API",
        "version": "1.2.1",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/v1/info")
async def get_system_info():
    """Получение информации о системе"""
    return {
        "version": "1.2.1",
        "python_version": sys.version,
        "dependencies": {
            "polars": "0.20.0",
            "pandas": "2.2.0",
            "numpy": "1.26.0",
            "fastapi": "0.100.0",
            "uvicorn": "0.20.0"
        }
    }


@app.post("/api/v1/calculate", response_model=CalculationResponse)
async def calculate_shrinkage(request: CalculationRequest):
    """
    Расчет усушки для предоставленных данных.
    """
    try:
        # Преобразуем данные в DataFrame
        data_dicts = [item.dict() for item in request.data]
        dataset = pd.DataFrame(data_dicts)
        
        # Создаем систему расчета
        system = ShrinkageSystem()
        
        # Устанавливаем процент излишка если указан
        if request.surplus_rate > 0:
            system.set_surplus_rate(request.surplus_rate / 100.0)
        
        # Обрабатываем набор данных
        results = system.process_dataset(
            dataset=dataset,
            source_filename="api_request",
            use_adaptive=request.use_adaptive_model
        )
        
        if results.get('status') == 'success':
            return CalculationResponse(
                status="success",
                data=results.get('data'),
                reports=results.get('reports'),
                message="Расчет успешно завершен"
            )
        else:
            error_msg = results.get('message', 'Неизвестная ошибка')
            raise HTTPException(status_code=400, detail=error_msg)
            
    except Exception as e:
        log.exception(f"Ошибка при расчете усушки: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_adaptive_model: bool = Form(False),
    surplus_rate: float = Form(0.0)
):
    """
    Загрузка Excel файла для расчета.
    """
    try:
        # Генерируем уникальный идентификатор задачи
        job_id = str(uuid.uuid4())
        
        # Создаем запись задачи
        jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "result": None,
            "error": None
        }
        
        # Сохраняем файл временно
        temp_dir = "temp"
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Запускаем фоновую обработку
        background_tasks.add_task(
            process_excel_background, 
            file_path, 
            job_id, 
            use_adaptive_model, 
            surplus_rate
        )
        
        return {
            "status": "success",
            "job_id": job_id,
            "message": "Файл загружен и обработка начата"
        }
        
    except Exception as e:
        log.exception(f"Ошибка при загрузке файла: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Получение статуса обработки файла.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    job = jobs[job_id]
    return JobStatus(**job)


@app.get("/api/v1/settings")
async def get_settings():
    """
    Получение текущих настроек системы.
    """
    settings_manager = SettingsManager()
    return settings_manager.get_all_settings()


@app.put("/api/v1/settings")
async def update_settings(settings: SettingsUpdate):
    """
    Обновление настроек системы.
    """
    try:
        settings_manager = SettingsManager()
        
        # Преобразуем модель в словарь и фильтруем None значения
        update_dict = {k: v for k, v in settings.dict().items() if v is not None}
        
        if update_dict:
            success = settings_manager.update_settings(update_dict)
            if success:
                settings_manager.save_settings()
                return {"status": "success", "message": "Настройки обновлены"}
            else:
                raise HTTPException(status_code=400, detail="Ошибка при обновлении настроек")
        else:
            return {"status": "success", "message": "Нет настроек для обновления"}
            
    except Exception as e:
        log.exception(f"Ошибка при обновлении настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics():
    """
    Получение метрик системы.
    """
    # Здесь можно добавить реальные метрики системы
    return {
        "uptime": "system_uptime",
        "total_requests": 0,
        "successful_calculations": 0,
        "failed_calculations": 0,
        "average_response_time": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")