# Parser Site

Базовый, но уже практичный каркас проекта для разработки парсера в новом окружении.

## Что уже готово

- Python-пакет `parser_site`
- Парсинг e-mail, URL и телефонов
- Нормализация данных (например, email в lower-case, очистка URL от конечной пунктуации, нормализация телефона)
- CLI с поддержкой текста, файла и stdin
- HTTP API (FastAPI) с endpoint `/parse`
- Автотесты на `pytest`

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m parser_site.cli "Контакты: dev@example.com, сайт: https://example.com, тел: +7 (999) 123-45-67"
```

## Использование CLI

```bash
# 1) Текстом
python -m parser_site.cli "mail: team@example.com, phone: +1-202-555-0182"

# 2) Из файла
python -m parser_site.cli --file sample.txt --pretty

# 3) Через stdin
cat sample.txt | python -m parser_site.cli

# 4) Только нужные поля
python -m parser_site.cli "a@example.com +1 202 555 0182" --only emails --only phones
```

## Коды возврата CLI

- `0` — успешный парсинг
- `2` — ошибка входных данных/чтения файла (сообщение выводится в stderr)

## HTTP API (FastAPI)

```bash
uvicorn parser_site.api:app --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

Пример запроса:

```bash
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"dev@example.com https://example.com +1 (202) 555-0182"}'
```

Ограничения API:

- Максимальный размер `text`: `100000` символов
- Таймаут обработки: `1.0` секунда

## Docker

```bash
docker build -t parser-site .
docker run --rm -p 8000:8000 parser-site
```

## Структура

- `src/parser_site/parser.py` — логика парсинга
- `src/parser_site/cli.py` — интерфейс командной строки
- `src/parser_site/api.py` — HTTP API
- `tests/test_parser.py` — тесты парсера
- `tests/test_cli.py` — тесты CLI
- `tests/test_api.py` — тесты API
