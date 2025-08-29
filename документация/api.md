# API документация системы расчета усушки

## Обзор

Система предоставляет REST API для интеграции с другими приложениями и автоматизации процессов расчета усушки.

## Запуск API сервера

```bash
# Запуск сервера разработки
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

# Запуск сервера в production
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## Аутентификация

API использует токенную аутентификацию. Для получения токена:

```bash
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Все запросы к API должны включать заголовок:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Эндпоинты

### 1. Расчет усушки

#### POST /api/v1/calculate

Запуск расчета усушки для предоставленных данных.

**Тело запроса:**

```json
{
  "data": [
    {
      "номенклатура": "Рыба треска",
      "дата_прихода": "2024-01-01",
      "дата_инвентаризации": "2024-01-15",
      "начальный_остаток": 1000,
      "конечный_остаток": 950,
      "единица_измерения": "кг"
    }
  ],
  "use_adaptive_model": true,
  "surplus_rate": 0.05
}
```

**Ответ:**

```json
{
  "status": "success",
  "data": {
    "coefficients": [
      {
        "номенклатура": "Рыба треска",
        "коэффициент_усушки": 0.0033,
        "точность": 95.5,
        "период_хранения": 14,
        "фактическая_усушка": 50,
        "прогнозируемая_усушка": 46.7
      }
    ],
    "summary": {
      "total_positions": 1,
      "avg_accuracy": 95.5,
      "error_count": 0
    }
  },
  "reports": {
    "coefficients": "/results/report_20240101_120000.html",
    "errors": "/results/errors_20240101_120000.html"
  }
}
```

### 2. Загрузка файла

#### POST /api/v1/upload

Загрузка Excel файла для расчета.

**Тело запроса (multipart/form-data):**

```
file: your_excel_file.xlsx
use_adaptive_model: true
surplus_rate: 0.05
```

**Ответ:**

```json
{
  "status": "success",
  "job_id": "abc123",
  "message": "Файл загружен и обработка начата"
}
```

### 3. Статус обработки

#### GET /api/v1/status/{job_id}

Получение статуса обработки файла.

**Ответ:**

```json
{
  "status": "completed",
  "progress": 100,
  "result": {
    "coefficients_report": "/results/report_20240101_120000.html",
    "errors_report": "/results/errors_20240101_120000.html"
  }
}
```

### 4. Получение отчета

#### GET /api/v1/reports/{report_id}

Получение HTML отчета по идентификатору.

### 5. Настройки

#### GET /api/v1/settings

Получение текущих настроек системы.

#### PUT /api/v1/settings

Обновление настроек системы.

**Тело запроса:**

```json
{
  "model_type": "exponential",
  "default_period": 7,
  "min_accuracy": 50.0,
  "use_adaptive_model": false
}
```

### 6. Системная информация

#### GET /api/v1/info

Получение информации о системе.

**Ответ:**

```json
{
  "version": "1.2.1",
  "python_version": "3.11.0",
  "dependencies": {
    "polars": "0.20.0",
    "pandas": "2.2.0",
    "numpy": "1.26.0"
  }
}
```

## Модели данных

### ShrinkageData

```json
{
  "номенклатура": "string",
  "дата_прихода": "date",
  "дата_инвентаризации": "date",
  "начальный_остаток": "number",
  "конечный_остаток": "number",
  "единица_измерения": "string"
}
```

### CoefficientResult

```json
{
  "номенклатура": "string",
  "коэффициент_усушки": "number",
  "точность": "number",
  "период_хранения": "integer",
  "фактическая_усушка": "number",
  "прогнозируемая_усушка": "number"
}
```

### CalculationRequest

```json
{
  "data": "ShrinkageData[]",
  "use_adaptive_model": "boolean",
  "surplus_rate": "number"
}
```

### CalculationResponse

```json
{
  "status": "string",
  "data": {
    "coefficients": "CoefficientResult[]",
    "summary": {
      "total_positions": "integer",
      "avg_accuracy": "number",
      "error_count": "integer"
    }
  },
  "reports": {
    "coefficients": "string",
    "errors": "string"
  }
}
```

## Ошибки

API возвращает стандартные HTTP коды ошибок:

- 200 - Успешный запрос
- 400 - Неверный запрос
- 401 - Неавторизованный доступ
- 404 - Ресурс не найден
- 500 - Внутренняя ошибка сервера

**Формат ошибки:**

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Описание ошибки",
    "details": "Дополнительная информация"
  }
}
```

## Примеры использования

### Python

```python
import requests

# Загрузка файла
with open('данные.xlsx', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/upload',
        files=files,
        data={'use_adaptive_model': 'true'}
    )

# Получение результата
job_id = response.json()['job_id']
result = requests.get(f'http://localhost:8000/api/v1/status/{job_id}')
```

### JavaScript

```javascript
// Расчет усушки
const data = {
  data: [{
    номенклатура: "Рыба треска",
    дата_прихода: "2024-01-01",
    дата_инвентаризации: "2024-01-15",
    начальный_остаток: 1000,
    конечный_остаток: 950,
    единица_измерения: "кг"
  }],
  use_adaptive_model: true
};

fetch('http://localhost:8000/api/v1/calculate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => console.log(result));
```

## Ограничения

- Максимальный размер загружаемого файла: 50 МБ
- Максимальное количество записей в одном запросе: 10000
- Максимальное время обработки: 300 секунд
- Частота запросов: 10 запросов в минуту на IP адрес

## Мониторинг и логирование

API автоматически логирует все запросы в файлы логов. Для мониторинга доступны метрики:

- Количество обработанных запросов
- Среднее время ответа
- Количество ошибок
- Использование ресурсов

Метрики доступны по адресу: `GET /api/v1/metrics`