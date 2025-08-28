#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели данных Pydantic для валидации JSON.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any

class GroupingInfo(BaseModel):
    row_groups: List[Any] = Field(default_factory=list)
    column_groups: List[Any] = Field(default_factory=list)
    row_outline_levels: Dict[str, int] = Field(default_factory=dict)
    column_outline_levels: Dict[str, int] = Field(default_factory=dict)

class JsonDataModel(BaseModel):
    source_file: str
    sheet_count: int
    sheets: Dict[str, List[List[Any]]]
    grouping_info: Dict[str, GroupingInfo]
