#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели данных Pydantic для валидации.

Этот файл определяет структуры данных, используемые в проекте,
для обеспечения их корректности и целостности.
"""

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from typing import List, Optional

class NomenclatureRow(BaseModel):
    """
    Валидирует одну строку данных о номенклатуре, готовую к расчету.
    """
    name: str = Field(..., alias='Номенклатура', description="Название номенклатурной позиции")
    initial_balance: PositiveFloat = Field(..., alias='Начальный_остаток')
    incoming: float = Field(..., alias='Приход', ge=0) # ge=0 означает "больше или равно 0"
    outgoing: float = Field(..., alias='Расход', ge=0)
    final_balance: float = Field(..., alias='Конечный_остаток', ge=0)
    storage_days: PositiveInt = Field(..., alias='Период_хранения_дней')

    class Config:
        # Позволяет модели работать, даже если в исходном словаре есть лишние поля
        extra = 'ignore' 
