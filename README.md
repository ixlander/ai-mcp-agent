"# AI MCP Agent

> AI Agent with MCP Integration - Enterprise-ready architecture for product management

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple.svg)](https://github.com/langchain-ai/langgraph)

## 📋 Описание проекта

Полнофункциональный AI-агент с интеграцией MCP (Model Context Protocol), который:
- Работает с кастомными инструментами (tools) через LangGraph
- Подключается к MCP серверу для управления данными о продуктах
- Обрабатывает естественные языковые запросы пользователя
- Предоставляет REST API для интеграции
- Запускается через Docker Compose

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Container                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │              FastAPI Application                  │  │
│  │          POST /api/v1/agent/query                 │  │
│  │       (Получает запросы пользователя)             │  │
│  └─────────────────────┬─────────────────────────────┘  │
│                        │                                │
│                        ▼                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │              LangGraph Agent                      │  │
│  │  • Анализирует запрос пользователя                │  │
│  │  • Выбирает подходящие tools                      │  │
│  │  • Вызывает tools и обрабатывает результаты       │  │
│  │  • Формирует ответ                                │  │
│  └───┬──────────────────────────────┬────────────────┘  │
│      │                              │                   │
│      ▼                              ▼                   │
│  ┌──────────────┐         ┌──────────────────────────┐  │
│  │ Custom Tools │         │   MCP Server             │  │
│  │              │         │  (stdio transport)       │  │
│  │ • Calculator │         │                          │  │
│  │ • Formatter  │         │ Tools:                   │  │
│  └──────────────┘         │ • list_products          │  │
│                           │ • get_product            │  │
│                           │ • add_product            │  │
│                           │ • get_statistics         │  │
│                           │                          │  │
│                           │ Storage:                 │  │
│                           │ • JSON file              │  │
│                           └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

**Требования:**
- Docker Engine 20.10+
- Docker Compose 2.0+

**Запуск:**

```bash
# 1. Клонируйте репозиторий (если нужно)
git clone <repo-url>
cd ai-mcp-agent

# 2. Запустите приложение
docker-compose up -d

# 3. Проверьте статус
docker-compose ps

# 4. Откройте API документацию
# http://localhost:8000/docs
```

**Остановка:**

```bash
docker-compose down
```

### Вариант 2: Локально (без Docker)

**Требования:**
- Python 3.11+
- pip или poetry

**Установка зависимостей:**

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

**Запуск MCP сервера:**

```bash
# В отдельном терминале
python -m mcp_server.mcp_server
```

**Запуск FastAPI приложения:**

```bash
# В основном терминале
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**API документация:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Query Agent

```http
POST /api/v1/agent/query
Content-Type: application/json

{
  "query": "Покажи все продукты в категории Электроника"
}
```

**Response:**
```json
{
  "query": "Покажи все продукты в категории Электроника",
  "response": "Products in Электроника: {...}",
  "status": "success"
}
```

### Examples

```http
GET /api/v1/examples
```

**Response:**
```json
{
  "examples": [
    {
      "query": "Покажи все продукты",
      "description": "Get all products"
    },
    ...
  ]
}
```

## 💬 Примеры использования

### Пример 1: Получить все продукты

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Покажи все продукты"}'
```

### Пример 2: Получить продукты по категории

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Покажи все продукты в категории Электроника"}'
```

### Пример 3: Получить статистику

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Какая средняя цена продуктов?"}'
```

### Пример 4: Посчитать скидку

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Посчитай скидку 15% на товар с ID 1"}'
```

### Пример 5: Найти продукт по ID

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Найди товар с ID 1"}'
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Запустите все тесты
pytest tests/ -v

# Запустите с покрытием
pytest tests/ --cov=app --cov=mcp_server

# Запустите конкретный тест
pytest tests/test_api.py::TestHealthEndpoint::test_health_check -v
```

### Доступные тесты

**test_agent.py:**
- `TestCalculatorTool` - Тесты калькулятора (3 теста)
- `TestFormatterTool` - Тесты форматтера (4 теста)
- `TestAgentProcessing` - Тесты обработки запросов (4 теста)
- `TestAgentIntegration` - Интеграционные тесты (3 теста)

**test_api.py:**
- `TestHealthEndpoint` - Тесты health check (2 теста)
- `TestQueryEndpoint` - Тесты query endpoint (6 тестов)
- `TestExamplesEndpoint` - Тесты examples endpoint (2 теста)
- `TestErrorHandling` - Тесты обработки ошибок (2 теста)
- `TestEndpoints` - Общие тесты endpoints (1 тест)

**Итого: 27+ тестов**

### Примеры результатов тестов

```
tests/test_agent.py::TestCalculatorTool::test_percentage_calculation PASSED
tests/test_agent.py::TestCalculatorTool::test_simple_arithmetic PASSED
tests/test_agent.py::TestFormatterTool::test_json_formatting PASSED
tests/test_api.py::TestHealthEndpoint::test_health_check PASSED
tests/test_api.py::TestQueryEndpoint::test_query_endpoint_basic PASSED
...
```

## 📦 Структура проекта

```
ai-mcp-agent/
├── app/                          # FastAPI приложение
│   ├── __init__.py
│   ├── main.py                  # FastAPI endpoints
│   └── agent.py                 # LangGraph агент
├── mcp_server/                   # MCP сервер
│   ├── __init__.py
│   └── mcp_server.py            # MCP сервер с FastMCP
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── test_agent.py            # Тесты агента
│   └── test_api.py              # Тесты API
├── data/                         # Данные
│   └── products.json            # Данные о продуктах
├── .gitignore                    # Git ignore файл
├── requirements.txt              # Python зависимости
├── Dockerfile                    # Docker конфигурация
├── docker-compose.yml            # Docker Compose конфигурация
└── README.md                     # Этот файл
```

## 🔧 Компоненты системы

### MCP Server (`mcp_server/mcp_server.py`)

**Использует:** FastMCP, JSON storage

**Инструменты (Tools):**
1. `list_products` - Получить список продуктов (опционально по категории)
2. `get_product` - Получить продукт по ID
3. `add_product` - Добавить новый продукт
4. `get_statistics` - Получить статистику по продуктам

**Особенности:**
- ✅ Работает через stdio транспорт
- ✅ Type hints для всех параметров
- ✅ Docstrings с описанием
- ✅ Обработка ошибок (ValueError)
- ✅ JSON сериализация данных

### LangGraph Agent (`app/agent.py`)

**Использует:** LangGraph, LangChain, Mock LLM

**Custom Tools:**
1. `calculator` - Расчет выражений и скидок
2. `formatter` - Форматирование текста (JSON, uppercase, lowercase)

**Особенности:**
- ✅ Интеграция с MCP сервером
- ✅ Обработка естественного языка
- ✅ Маршрутизация запросов к нужным tools
- ✅ Mock LLM без реальных API ключей

### FastAPI Application (`app/main.py`)

**Endpoints:**
1. `GET /health` - Health check
2. `POST /api/v1/agent/query` - Запрос к агенту
3. `GET /api/v1/examples` - Примеры запросов

**Особенности:**
- ✅ Type-safe с Pydantic моделями
- ✅ CORS поддержка
- ✅ Логирование
- ✅ Error handling
- ✅ Swagger/ReDoc документация

## 🐳 Docker

### Dockerfile особенности

- **Multi-stage build** - оптимизация размера образа
- **Health checks** - автоматическая проверка здоровья контейнера
- **Slim base image** - минимальный размер (от 120MB)

### Docker Compose сервисы

1. **api** - FastAPI приложение на порту 8000
2. **mcp-server** - MCP сервер на порту 3001

**Volumes:**
- `./data` - persistent data
- `./app` - код приложения
- `./mcp_server` - код MCP сервера

## 📊 Поддерживаемые типы запросов

| Тип | Пример | Результат |
|-----|--------|----------|
| Список продуктов | "Покажи все продукты" | Полный список |
| По категории | "Продукты в категории Электроника" | Отфильтрованный список |
| Статистика | "Какая средняя цена?" | Статистика |
| По ID | "Найди товар с ID 1" | Конкретный продукт |
| Расчеты | "Посчитай 15% скидку" | Результат расчета |

## 🔐 Безопасность

**Реализованные меры:**
- ✅ Type validation с Pydantic
- ✅ Error handling и logging
- ✅ CORS защита
- ✅ Validation при добавлении данных

**Рекомендации для production:**
- Добавить аутентификацию (JWT, OAuth2)
- Использовать HTTPS
- Добавить rate limiting
- Настроить firewall правила

## 🛠️ Разработка

### Добавление нового tool

**В MCP сервере:**
```python
@server.tool()
def my_tool(param: str) -> dict:
    """Tool description."""
    return {"result": "value"}
```

**В агенте:**
```python
@tool
def my_custom_tool(param: str) -> str:
    """Custom tool description."""
    return f"Result: {param}"
```

### Добавление нового endpoint

```python
@app.post("/api/v1/my-endpoint")
async def my_endpoint(request: MyRequest) -> MyResponse:
    """Endpoint description."""
    # Implementation
    return response
```

## 🐛 Troubleshooting

### Проблема: Port already in use

```bash
# Освободите порт
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>
```

### Проблема: ModuleNotFoundError

```bash
# Убедитесь что виртуальное окружение активировано
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

### Проблема: Docker образ не собирается

```bash
# Очистите Docker кэш
docker-compose down -v
docker system prune -a

# Пересоберите
docker-compose build --no-cache
```

## 📚 Дополнительные ресурсы

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

## 📄 Лицензия

MIT License - свободен для использования в образовательных целях

---

**Версия:** 1.0.0" 
