# Урок 2: RAG с LangChain

Отдельный проект: Markdown → Document → фрагменты → OllamaEmbeddings →
PGVector в Supabase → Retriever → ChatPromptTemplate → ChatOllama.

## Подготовка

Из корня репозитория установи зависимости в интерпретатор проекта:

```powershell
.\.venv\Scripts\python.exe -m pip install -r langchain_rag/requirements.txt
Copy-Item langchain_rag/.env.example langchain_rag/.env
```

В `.env` уже указаны параметры существующей Supabase. Пароль можно вводить
при каждом запуске или указать в `PGPASSWORD`. `.env` исключён из Git.
При вводе в консоли пароль виден.

Для генерации ответа укажи `CHAT_MODEL`: название установленной разговорной
модели Ollama (посмотри `ollama list`). `embeddinggemma` создаёт векторы,
но не генерирует ответы. Ollama должен быть запущен.

## Запуск из корня репозитория

```powershell
.\.venv\Scripts\python.exe langchain_rag/app.py index
.\.venv\Scripts\python.exe langchain_rag/app.py search "How does asyncio handle network waiting?"
.\.venv\Scripts\python.exe langchain_rag/app.py ask "How does asyncio handle network waiting?"
```

В PyCharm также можно запускать `app.py`, указав эти аргументы в конфигурации запуска.

Пока добавлен один учебный документ `documents/asyncio.md`.
Документы компании из урока можно будет добавить в эту папку позже.
Загрузка повторно использует id неизменённых фрагментов. При редактировании
или удалении файлов старые фрагменты автоматически не удаляются.

LangChain создаст свои таблицы `langchain_pg_collection` и `langchain_pg_embedding`
и коллекцию `lesson2_langchain`. Таблицы первого урока не используются.
Первый запуск `index`, `search` или `ask` создаёт таблицы/коллекцию при необходимости.

Документация: [PGVector](https://reference.langchain.com/python/langchain-postgres/vectorstores/PGVector),
[ChatOllama](https://reference.langchain.com/python/langchain-ollama/chat_models/ChatOllama).
