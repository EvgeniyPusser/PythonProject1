# Урок 2: Company Knowledge Assistant

LangChain + Ollama + PostgreSQL/pgvector в существующей Supabase.
Docker для этого проекта не нужен.

```text
langchain_rag/
├── requirements.txt
├── .env.example
├── knowledge/
│   ├── employee_handbook.md
│   ├── it_security_policy.md
│   └── travel_policy.md
└── src/
    ├── config.py
    ├── knowledge.py
    ├── vector_store.py
    ├── index_documents.py
    └── rag.py
```

Три документа описывают вымышленную BluePeak Systems и перенесены из текста урока.
Код первого урока находится отдельно в корневой папке `src`.

## Настройка

Зависимости уже установлены в `.venv` проекта. Для повторной установки из корня:

```powershell
.\.venv\Scripts\python.exe -m pip install -r langchain_rag/requirements.txt
```

Локальный `langchain_rag/.env` уже создан из `.env.example`; он исключён из Git.
Пароль можно оставить пустым и вводить при запуске (в консоли он будет виден).
Для нового checkout скопируй `.env.example` в `.env`.

Используется существующая Supabase с уже включённым pgvector.
LangChain создаёт свои таблицы `langchain_pg_collection`, `langchain_pg_embedding`
и отдельную коллекцию `lesson2_langchain`. Таблицы первого урока не используются.

Модель embeddings — `embeddinggemma`. Разговорная модель — установленная
`phi3:latest`. В уроке используется `gemma3:4b`: чтобы переключиться, сначала
установи её в Ollama, затем измени `CHAT_MODEL` в `.env`.
Автоматически новая модель не скачивается.

## Шаг 1. Загрузка и разбиение без обращения к базе

Из корня репозитория:

```powershell
.\.venv\Scripts\python.exe langchain_rag/src/knowledge.py
```

Должно быть `Documents: 3`. Далее печатаются фрагменты с `source` и `start_index`.
Параметры по умолчанию: `CHUNK_SIZE=600`, `CHUNK_OVERLAP=100`, `TOP_K=3`.
Их можно изменить в `.env`.

## Шаг 2. Индексация в Supabase

```powershell
.\.venv\Scripts\python.exe langchain_rag/src/index_documents.py
```

`add_documents()` получает embeddings и сохраняет текст, метаданные и векторы.
Стабильные id предотвращают копии неизменённых фрагментов при повторной загрузке.
Если документы или настройки разбиения изменились, старые фрагменты сами не удаляются.
Для полного пересоздания только этой коллекции используй явно:

```powershell
.\.venv\Scripts\python.exe langchain_rag/src/index_documents.py --recreate
```

## Шаг 3. Проверка поиска без генерации

```powershell
.\.venv\Scripts\python.exe langchain_rag/src/rag.py --search-only 'Do I need a receipt for a $40 taxi ride?'
```

Ожидается фрагмент из `travel_policy.md` с правилом о чеках для расходов свыше $25.

## Шаг 4. RAG

```powershell
.\.venv\Scripts\python.exe langchain_rag/src/rag.py
```

Вопросы вводятся по одному, `exit` завершает программу. Пароль запрашивается один раз.
История диалога не хранится: каждый вопрос независим.

Для одного вопроса с выводом найденного контекста:

```powershell
.\.venv\Scripts\python.exe langchain_rag/src/rag.py --debug "How many vacation days do full-time employees receive?"
```

`Retriever` возвращает Top K фрагментов. `format_documents` добавляет имена
источников и позиции. `ChatPromptTemplate | ChatOllama | StrOutputParser`
формирует ответ. Найденные источники выводятся отдельно от ответа модели.

Проверь также вопрос про parental leave: сведений об этом в документах нет.
Промпт требует `I don't know based on the provided documents.`
Это инструкция модели, а не гарантия правильного отказа: проверяй ответ и контекст.

В PyCharm можно запускать файлы из `langchain_rag/src` через Run.
Аргументы `--search-only`, `--debug` и `--recreate` задаются в конфигурации запуска.

## Соответствие уроку

Сохранены Document, RecursiveCharacterTextSplitter с `add_start_index=True`,
OllamaEmbeddings, PGVector с 768 измерениями и cosine distance, Retriever,
ChatPromptTemplate, ChatOllama, StrOutputParser и CLI с источниками.
Вместо localhost используется Supabase, вместо автоматического удаления
коллекции при каждом запуске — явный флаг `--recreate`.

Документация: [PGVector](https://reference.langchain.com/python/langchain-postgres/vectorstores/PGVector),
[ChatOllama](https://reference.langchain.com/python/langchain-ollama/chat_models/ChatOllama).
