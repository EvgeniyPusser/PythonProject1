# Урок 3 — RAG Knowledge Assistant

Backend: FastAPI + LangChain + локальная Ollama + облачная Supabase/pgvector.
Frontend пока содержит только заготовки.

Все команды ниже выполняются из корня `PythonProject1` в терминале PyCharm.

## Запуск API

```text
./.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir rag-knowledge-assistant/backend --reload
```

Открой http://localhost:8000/docs и используй **Try it out** → **Execute**.

* `GET /api/health` — проверка работы API (не проверяет внешние сервисы).
* `GET /api/documents` — список файлов.
* `POST /api/documents` — загрузка UTF-8 `.md`/`.txt`, до 1 000 000 байт.
* `DELETE /api/documents/{filename}` — удаление файла.
* `POST /api/ask` — вопрос и ответ с найденными источниками.

Пример тела запроса:

```json
{"question": "Do I need a receipt for a $40 taxi ride?"}
```

## Подключение

Пароль Supabase читается из `backend/.env` (файл исключён из Git):

```dotenv
PGPASSWORD='your_password'
```

Если пароль не заполнен, программа запросит его в терминале при первом обращении к БД.
Ollama должна работать на `http://localhost:11434`, модели — `embeddinggemma` и `phi3:latest`.
Используется отдельная коллекция `lesson3_knowledge`; коллекция второго урока не пересоздаётся.

## Первичная индексация

Из папки `rag-knowledge-assistant/backend`:

```text
../../.venv/Scripts/python.exe -m app.index_documents
```

После загрузки или удаления файла API полностью пересоздаёт коллекцию.
Это учебная стратегия: при ошибке индексации оригинальный файл восстанавливается,
но индекс может быть неполным; устрани причину ошибки и запусти индексацию повторно.
Запускай один процесс API: блокировка перестройки действует внутри одного процесса.
