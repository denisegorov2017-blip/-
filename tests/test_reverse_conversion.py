#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование обратной конвертации из JSON в Excel с сохранением иерархии
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path



from src.core.excel_hierarchy_preserver import json_to_excel as preserver_json_to_excel

def test_reverse_conversion():
    """Тестирование обратной конвертации из JSON в Excel."""
    # Создаем директорию результатов если она не существует
    os.makedirs("результаты", exist_ok=True)
    
    # Тестовые данные
    test_excel_file = "результаты/hierarchy_test_file.xlsx"
    json_file = "результаты/hierarchy_test.json"
    restored_excel_file = "результаты/restored_from_json.xlsx"

    # 1. Создаем тестовый Excel-файл
    data1 = {'col1': [1, 2], 'col2': ['A', 'B']}
    data2 = {'colA': [3, 4], 'colB': ['C', 'D']}
    with pd.ExcelWriter(test_excel_file) as writer:
        pd.DataFrame(data1).to_excel(writer, sheet_name='Sheet1', index=False)
        pd.DataFrame(data2).to_excel(writer, sheet_name='Sheet2', index=False)

    # 2. Конвертируем Excel в JSON
    from src.core.excel_hierarchy_preserver import ExcelHierarchyPreserver
    preserver = ExcelHierarchyPreserver(test_excel_file)
    preserver.to_json(json_file)

    # 3. Конвертируем JSON обратно в Excel
    result = preserver_json_to_excel(json_file, restored_excel_file)
    assert result, "Ошибка восстановления из JSON"

    # 4. Проверяем, что файлы существуют
    assert os.path.exists(test_excel_file), "Исходный файл не создан"
    assert os.path.exists(json_file), "JSON файл не создан"
    assert os.path.exists(restored_excel_file), "Восстановленный файл не создан"

    print("✅ Все проверки пройдены успешно!")


