# RAG Fundamentals — Lesson 3

## Building a Full-Stack RAG Knowledge Assistant with FastAPI and React

---

# 1. Learning Objectives

By the end of this lesson, you should be able to:

* turn the RAG pipeline from Lesson 2 into a reusable backend service;
* expose RAG functionality through a REST API;
* accept document uploads with FastAPI;
* validate uploaded files;
* rebuild a vector knowledge base after document changes;
* expose document-management endpoints;
* expose an endpoint for RAG questions;
* understand why synchronous RAG operations should not be placed carelessly inside an `async` endpoint;
* configure CORS for a React frontend;
* connect a React application to the FastAPI backend;
* upload documents from the browser;
* ask questions from the browser;
* display generated answers and retrieved sources;
* delete documents and rebuild the knowledge base;
* understand the difference between a classroom indexing strategy and production incremental indexing;
* switch the generation model from local Ollama to an Ollama Cloud model.

At the end of the lesson, we will have a complete application:

```text
React
   │
   │ HTTP
   ▼
FastAPI
   │
   ├──────── LangChain RAG
   │              │
   │              ├── Ollama Embeddings
   │              ├── Ollama LLM
   │              └── PGVector
   │
   ▼
PostgreSQL + pgvector
```

---

# 2. What We Have Built So Far

## Lesson 1

We built semantic retrieval manually:

```text
Text
 ↓
Embedding
 ↓
Vector
 ↓
pgvector
 ↓
Relevant Documents
```

---

## Lesson 2

We built a complete RAG pipeline:

```text
Documents
   ↓
Chunks
   ↓
Embeddings
   ↓
Vector Store

Question
   ↓
Retriever
   ↓
Relevant Chunks
   ↓
Prompt
   ↓
LLM
   ↓
Answer
```

But the application was still a command-line program:

```text
Question: ...
Answer: ...
Sources: ...
```

---

# 3. Goal of Lesson 3

We now want users to work with the RAG system through a browser.

The final application will support:

```text
Upload Document
       │
       ▼
Add to Knowledge Base
```

```text
Ask Question
       │
       ▼
RAG
       │
       ▼
Answer + Sources
```

and:

```text
Delete Document
       │
       ▼
Update Knowledge Base
```

The UI will look conceptually like this:

```text
┌─────────────────────────────────────────────────────────┐
│ BluePeak Knowledge Assistant                            │
│                                                         │
│ Knowledge Base                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ employee_handbook.md                         Delete │ │
│ │ it_security_policy.md                       Delete │ │
│ │ travel_policy.md                            Delete │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [ Choose file ] [ Upload ]                              │
│                                                         │
│ Ask a Question                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Do I need a receipt for a $40 taxi ride?           │ │
│ └─────────────────────────────────────────────────────┘ │
│                                              [ Ask ]    │
│                                                         │
│ Answer                                                  │
│ Yes. Receipts are required for expenses above $25.     │
│                                                         │
│ Sources                                                 │
│ travel_policy.md                                        │
└─────────────────────────────────────────────────────────┘
```

---

# 4. Application Architecture

We will separate the application into three layers:

```text
┌──────────────────────────────┐
│          React UI            │
│                              │
│ upload / ask / delete        │
└──────────────┬───────────────┘
               │ HTTP / JSON
               ▼
┌──────────────────────────────┐
│         FastAPI API          │
│                              │
│ REST endpoints               │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         RAG Service          │
│                              │
│ Load                         │
│ Split                        │
│ Embed                        │
│ Retrieve                     │
│ Generate                     │
└───────┬───────────┬──────────┘
        │           │
        ▼           ▼
     Ollama      PostgreSQL
                  + pgvector
```

This separation is important:

```text
React
```

does not need to know anything about embeddings.

FastAPI does not need to know how React renders the answer.

The RAG service does not need to know anything about HTML.

---

# 5. Project Structure

Create a new project:

```text
rag-knowledge-assistant/
│
├── docker-compose.yml
│
├── backend/
│   │
│   ├── requirements.txt
│   │
│   ├── knowledge/
│   │   ├── employee_handbook.md
│   │   ├── it_security_policy.md
│   │   └── travel_policy.md
│   │
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── schemas.py
│       ├── knowledge.py
│       ├── vector_store.py
│       ├── rag_service.py
│       ├── index_documents.py
│       └── main.py
│
└── frontend/
    ├── package.json
    └── src/
        ├── api.js
        ├── App.jsx
        ├── main.jsx
        └── index.css
```

The knowledge documents from Lesson 2 can be copied into:

```text
backend/knowledge/
```

---

# 6. PostgreSQL + pgvector

We continue using the same Docker Compose configuration:

```yaml
services:

  postgres:
    image: pgvector/pgvector:0.8.6-pg17

    container_name: rag-postgres

    environment:
      POSTGRES_DB: rag_course
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: rag_password

    ports:
      - "5432:5432"

    volumes:
      - pgvector_data:/var/lib/postgresql/data


volumes:
  pgvector_data:
```

Start PostgreSQL:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

---

# 7. Backend Dependencies

Create:

```text
backend/requirements.txt
```

```text
fastapi
uvicorn[standard]
python-multipart
langchain
langchain-ollama
langchain-postgres
langchain-text-splitters
psycopg[binary]
```

Install:

```bash
cd backend
```

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -r requirements.txt
```

FastAPI requires `python-multipart` when receiving uploaded files sent as form data.

---

# 8. Ollama Models

We continue using:

```text
embeddinggemma
```

for embeddings and:

```text
gemma3:4b
```

for generation.

Check:

```bash
ollama list
```

If necessary:

```bash
ollama pull embeddinggemma
```

```bash
ollama pull gemma3:4b
```

LangChain provides the current Ollama integrations through `OllamaEmbeddings` and `ChatOllama`.

---

# 9. Configuration

Create:

```text
backend/app/config.py
```

```python
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = BACKEND_ROOT / "knowledge"


DB_URL = (
    "postgresql+psycopg://"
    "rag_user:rag_password"
    "@localhost:5432/"
    "rag_course"
)


EMBEDDING_MODEL = "embeddinggemma"
EMBEDDING_DIMENSION = 768

CHAT_MODEL = "gemma3:4b"

COLLECTION_NAME = "company_knowledge"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

TOP_K = 3


ALLOWED_EXTENSIONS = {
    ".md",
    ".txt",
}

MAX_UPLOAD_BYTES = 1_000_000


CORS_ORIGINS = [
    "http://localhost:5173",
]
```

For this classroom project we support:

```text
Markdown
TXT
```

only.

PDF parsing is a separate concern and can be added later.

---

# 10. API Data Models

Create:

```text
backend/app/schemas.py
```

```python
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )


class SourceInfo(BaseModel):
    source: str
    start_index: int | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]


class DocumentInfo(BaseModel):
    name: str
    size: int


class IndexResponse(BaseModel):
    filename: str
    documents: int
    chunks: int
```

The browser will send:

```json
{
  "question": "How many vacation days do employees receive?"
}
```

and receive:

```json
{
  "answer": "Full-time employees receive 24 working days...",
  "sources": [
    {
      "source": "employee_handbook.md",
      "start_index": 0
    }
  ]
}
```

---

# 11. Why Define Response Models?

Instead of returning arbitrary dictionaries everywhere, we define an API contract.

For example:

```text
POST /api/ask
```

has:

```text
Request
   ↓
AskRequest
```

and:

```text
Response
   ↓
AskResponse
```

This gives the frontend a predictable structure.

---

# 12. Reuse the Document Loading Pipeline

Create:

```text
backend/app/knowledge.py
```

```python
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from .config import (
    ALLOWED_EXTENSIONS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    KNOWLEDGE_DIR,
)


def get_knowledge_files():
    return sorted(
        path
        for path in KNOWLEDGE_DIR.iterdir()
        if (
            path.is_file()
            and path.suffix.lower()
            in ALLOWED_EXTENSIONS
        )
    )


def load_documents() -> list[Document]:

    documents = []

    for path in get_knowledge_files():

        content = path.read_text(
            encoding="utf-8"
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": path.name,
                },
            )
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )

    return splitter.split_documents(
        documents
    )
```

This code should already be familiar from Lesson 2.

---

# 13. The Important Architectural Change

In Lesson 2, indexing was performed once:

```text
run index_documents.py
        ↓
knowledge base ready
```

But now users can upload documents while the application is running.

Therefore our system needs:

```text
Upload File
    ↓
Save File
    ↓
Update Vector Store
```

---

# 14. Classroom Strategy: Rebuild the Collection

There are two possible strategies.

## Production-Oriented Strategy

```text
Upload Document
      ↓
Split only this document
      ↓
Create only new embeddings
      ↓
Add new chunks
```

Deletion:

```text
Delete Document
      ↓
Delete only its chunks
```

This is called:

```text
incremental indexing
```

LangChain's vector-store interface supports adding and deleting documents, which makes incremental indexing possible.

---

## Strategy Used in This Lesson

Our knowledge base is very small.

Therefore we use:

```text
Upload/Delete
      ↓
Reload all files
      ↓
Recreate all chunks
      ↓
Recreate vector collection
```

This is less efficient but much easier to understand.

For a classroom application:

```text
few files
```

this is acceptable.

For:

```text
millions of chunks
```

it would be a bad design.

---

# 15. Vector Store

Create:

```text
backend/app/vector_store.py
```

```python
from langchain_ollama import (
    OllamaEmbeddings,
)

from langchain_postgres.vectorstores import (
    DistanceStrategy,
    PGVector,
)

from .config import (
    COLLECTION_NAME,
    DB_URL,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
)


embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL
)


def get_vector_store(
    recreate: bool = False,
) -> PGVector:

    return PGVector(
        embeddings=embeddings,
        connection=DB_URL,
        collection_name=COLLECTION_NAME,
        embedding_length=(
            EMBEDDING_DIMENSION
        ),
        distance_strategy=(
            DistanceStrategy.COSINE
        ),
        use_jsonb=True,
        pre_delete_collection=recreate,
    )
```

`langchain-postgres` provides the LangChain PostgreSQL vector-store integration using pgvector.

---

# 16. Create the RAG Service

Create:

```text
backend/app/rag_service.py
```

Start with imports:

```python
from langchain_core.documents import Document
from langchain_core.output_parsers import (
    StrOutputParser,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_ollama import ChatOllama

from .config import (
    CHAT_MODEL,
    KNOWLEDGE_DIR,
    TOP_K,
)

from .knowledge import (
    get_knowledge_files,
    load_documents,
    split_documents,
)

from .vector_store import (
    get_vector_store,
)
```

---

# 17. Configure the LLM

Add:

```python
llm = ChatOllama(
    model=CHAT_MODEL,
    temperature=0,
)
```

`ChatOllama` accepts chat-style input and provides the LangChain interface to models running through Ollama.

---

# 18. Reuse the Prompt

```python
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a company knowledge assistant.

Answer the user's question using only
the provided context.

If the context does not contain enough
information to answer, say exactly:

I don't know based on the provided documents.

Do not invent company policies.

Keep the answer concise and factual.
            """.strip(),
        ),

        (
            "human",
            """
Context:

{context}

Question:

{question}
            """.strip(),
        ),
    ]
)
```

---

# 19. Create the Generation Chain

```python
answer_chain = (
    prompt
    | llm
    | StrOutputParser()
)
```

Again:

```text
Prompt
  ↓
ChatOllama
  ↓
AIMessage
  ↓
String
```

---

# 20. Format Retrieved Documents

```python
def format_documents(
    documents: list[Document],
) -> str:

    parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        source = document.metadata.get(
            "source",
            "unknown",
        )

        start_index = (
            document.metadata.get(
                "start_index"
            )
        )

        parts.append(
            f"""
[Source {index}: {source},
 start_index={start_index}]

{document.page_content}
            """.strip()
        )

    return "\n\n---\n\n".join(parts)
```

---

# 21. Rebuild the Vector Index

Add:

```python
def rebuild_index() -> tuple[int, int]:

    documents = load_documents()

    chunks = split_documents(
        documents
    )

    vector_store = get_vector_store(
        recreate=True
    )

    if chunks:

        vector_store.add_documents(
            documents=chunks
        )

    return (
        len(documents),
        len(chunks),
    )
```

Architecture:

```text
knowledge/
   │
   ▼
load_documents()
   │
   ▼
split_documents()
   │
   ▼
chunks
   │
   ▼
OllamaEmbeddings
   │
   ▼
PGVector
```

---

# 22. Ask a Question

Add:

```python
def ask_question(
    question: str,
) -> tuple[str, list[dict]]:

    vector_store = get_vector_store()

    retriever = (
        vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": TOP_K,
            },
        )
    )

    documents = retriever.invoke(
        question
    )

    context = format_documents(
        documents
    )

    answer = answer_chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    sources = []

    seen = set()

    for document in documents:

        source = document.metadata.get(
            "source",
            "unknown",
        )

        start_index = (
            document.metadata.get(
                "start_index"
            )
        )

        key = (
            source,
            start_index,
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "source": source,
                "start_index": start_index,
            }
        )

    return answer, sources
```

---

# 23. The RAG Service Is Now Independent of HTTP

Notice that:

```python
ask_question(...)
```

does not know anything about FastAPI.

Likewise:

```python
rebuild_index(...)
```

does not know anything about React.

This is intentional.

```text
HTTP Layer
    │
    ▼
RAG Service
    │
    ▼
LangChain / Ollama / PostgreSQL
```

This makes the code easier to test and reuse.

---

# 24. Index Existing Documents

Create:

```text
backend/app/index_documents.py
```

```python
from .rag_service import (
    rebuild_index,
)


def main() -> None:

    documents, chunks = (
        rebuild_index()
    )

    print(
        f"Indexed {documents} documents "
        f"and {chunks} chunks."
    )


if __name__ == "__main__":
    main()
```

Run from:

```text
backend/
```

with:

```bash
python -m app.index_documents
```

---

# 25. Build the FastAPI Application

Create:

```text
backend/app/main.py
```

Start with:

```python
from pathlib import Path

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from .config import (
    ALLOWED_EXTENSIONS,
    CORS_ORIGINS,
    KNOWLEDGE_DIR,
    MAX_UPLOAD_BYTES,
)

from .knowledge import (
    get_knowledge_files,
)

from .rag_service import (
    ask_question,
    rebuild_index,
)

from .schemas import (
    AskRequest,
    AskResponse,
    DocumentInfo,
    IndexResponse,
)
```

---

# 26. Create the Application

```python
app = FastAPI(
    title=(
        "BluePeak Knowledge Assistant API"
    )
)
```

FastAPI automatically exposes OpenAPI-based API documentation for declared path operations.

---

# 27. CORS

Add:

```python
app.add_middleware(
    CORSMiddleware,

    allow_origins=CORS_ORIGINS,

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)
```

Why is this necessary?

Our React application runs at:

```text
http://localhost:5173
```

while FastAPI runs at:

```text
http://localhost:8000
```

An origin includes protocol, host, and port, so these are different browser origins. FastAPI recommends configuring `CORSMiddleware` when browser JavaScript communicates with a backend on another origin.

---

# 28. Health Endpoint

```python
@app.get("/api/health")
def health():
    return {
        "status": "ok",
    }
```

Test later with:

```text
GET /api/health
```

Expected:

```json
{
  "status": "ok"
}
```

---

# 29. List Documents

Add:

```python
@app.get(
    "/api/documents",
    response_model=list[DocumentInfo],
)
def list_documents():

    return [
        DocumentInfo(
            name=path.name,
            size=path.stat().st_size,
        )
        for path
        in get_knowledge_files()
    ]
```

The React frontend can now request:

```text
GET /api/documents
```

and receive:

```json
[
  {
    "name": "employee_handbook.md",
    "size": 1842
  },
  {
    "name": "travel_policy.md",
    "size": 1321
  }
]
```

---

# 30. Uploading Files with FastAPI

FastAPI provides `UploadFile` specifically for uploaded files. It exposes information such as the original filename and a file-like object containing the uploaded content.

Add:

```python
@app.post(
    "/api/documents",
    response_model=IndexResponse,
)
def upload_document(
    file: UploadFile,
):
```

Notice that this endpoint uses:

```python
def
```

rather than:

```python
async def
```

We will return to this decision shortly.

---

# 31. Do Not Trust the Uploaded Filename

A client controls:

```python
file.filename
```

so we should not directly use it as a filesystem path.

Add:

```python
    original_name = (
        file.filename or ""
    )

    filename = Path(
        original_name
    ).name
```

`Path(...).name` removes directory components.

For example, a value conceptually similar to:

```text
../../some_file.txt
```

becomes only its final filename component.

---

# 32. Validate the Filename

```python
    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Missing filename.",
        )
```

---

# 33. Validate the File Extension

```python
    suffix = (
        Path(filename)
        .suffix
        .lower()
    )

    if suffix not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only .md and .txt "
                "files are supported."
            ),
        )
```

For the lesson we intentionally limit the supported formats.

---

# 34. Limit File Size

```python
    raw = file.file.read(
        MAX_UPLOAD_BYTES + 1
    )
```

Then:

```python
    if len(raw) > MAX_UPLOAD_BYTES:

        raise HTTPException(
            status_code=413,
            detail="File is too large.",
        )
```

Our classroom application reads the uploaded text file into memory.

For very large uploads, a production design should use a streaming or more deliberate storage strategy instead.

---

# 35. Decode Text

```python
    try:

        content = raw.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail=(
                "File must contain "
                "UTF-8 text."
            ),
        )
```

---

# 36. Save the File

```python
    path = (
        KNOWLEDGE_DIR
        / filename
    )

    path.write_text(
        content,
        encoding="utf-8",
    )
```

Now:

```text
Browser Upload
     ↓
FastAPI
     ↓
backend/knowledge/file.md
```

---

# 37. Rebuild the Knowledge Base

Immediately after saving:

```python
    documents, chunks = (
        rebuild_index()
    )
```

Then return:

```python
    return IndexResponse(
        filename=filename,
        documents=documents,
        chunks=chunks,
    )
```

Complete flow:

```text
POST /api/documents
        │
        ▼
Validate File
        │
        ▼
Save File
        │
        ▼
Load All Documents
        │
        ▼
Split
        │
        ▼
Embed
        │
        ▼
Rebuild PGVector Collection
```

---

# 38. Why We Use a Normal `def` Endpoint

FastAPI supports both:

```python
async def
```

and:

```python
def
```

path operations.

Our current code uses synchronous operations such as:

```text
file.file.read()
LangChain sync methods
Ollama sync calls
PGVector sync calls
```

FastAPI's `UploadFile` documentation explicitly notes that the underlying `file` object is useful from regular synchronous `def` path operations.

Writing:

```python
async def endpoint():
    some_blocking_sync_function()
```

does **not** automatically make the blocking function asynchronous.

For this lesson, keeping the endpoint synchronous is the simpler and safer design.

---

# 39. Delete a Document

Add:

```python
@app.delete(
    "/api/documents/{filename}"
)
def delete_document(
    filename: str,
):

    safe_name = Path(filename).name

    path = (
        KNOWLEDGE_DIR
        / safe_name
    )

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if (
        path.suffix.lower()
        not in ALLOWED_EXTENSIONS
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid document.",
        )

    path.unlink()

    documents, chunks = (
        rebuild_index()
    )

    return {
        "deleted": safe_name,
        "documents": documents,
        "chunks": chunks,
    }
```

Again:

```text
Delete File
    ↓
Rebuild Collection
```

---

# 40. Ask Endpoint

Add:

```python
@app.post(
    "/api/ask",
    response_model=AskResponse,
)
def ask(
    request: AskRequest,
):

    answer, sources = (
        ask_question(
            request.question
        )
    )

    return AskResponse(
        answer=answer,
        sources=sources,
    )
```

This endpoint is deliberately very small.

It only translates:

```text
HTTP
 ↓
RAG Service
```

and:

```text
RAG Service Result
 ↓
HTTP Response
```

---

# 41. Complete API

Our backend now exposes:

| Method   | Endpoint                    | Purpose                 |
| -------- | --------------------------- | ----------------------- |
| `GET`    | `/api/health`               | Check backend           |
| `GET`    | `/api/documents`            | List knowledge files    |
| `POST`   | `/api/documents`            | Upload and index a file |
| `DELETE` | `/api/documents/{filename}` | Delete a file           |
| `POST`   | `/api/ask`                  | Ask the RAG system      |

This is the application boundary consumed by React.

---

# 42. Run FastAPI

From:

```text
backend/
```

run:

```bash
uvicorn app.main:app --reload
```

By default the development server is available at:

```text
http://localhost:8000
```

Open:

```text
http://localhost:8000/docs
```

and test the API before building the frontend.

---

# 43. Why Test the Backend First?

We now have two independent systems:

```text
React
```

and:

```text
FastAPI
```

If the final UI does not work, we need to know where the problem is.

Therefore first verify:

```text
FastAPI
   ↓
RAG
   ↓
works independently
```

Then connect React.

This makes debugging much easier.

---

# 44. Test `GET /api/documents`

Using Swagger UI:

```text
GET /api/documents
```

Expected result:

```json
[
  {
    "name": "employee_handbook.md",
    "size": 1820
  }
]
```

---

# 45. Test `POST /api/ask`

Request:

```json
{
  "question": "How many vacation days do employees receive?"
}
```

Expected structure:

```json
{
  "answer": "Full-time employees receive 24 working days...",
  "sources": [
    {
      "source": "employee_handbook.md",
      "start_index": 0
    }
  ]
}
```

---

# 46. Test Unknown Information

Request:

```json
{
  "question": "What is the parental leave policy?"
}
```

Expected:

```text
I don't know based on the provided documents.
```

Do not proceed to the frontend until the backend works correctly.

---

# 47. Create the React Application

Return to the project root:

```bash
cd ..
```

Create a Vite React project:

```bash
npm create vite@latest frontend -- --template react
```

Then:

```bash
cd frontend
```

```bash
npm install
```

Vite's official scaffolding tool supports creating framework-specific templates, including React, and the generated project uses `npm run dev` for its development server.

---

# 48. Start the Frontend

```bash
npm run dev
```

The development server normally displays a URL such as:

```text
http://localhost:5173
```

We already allowed this origin in FastAPI:

```python
CORS_ORIGINS = [
    "http://localhost:5173",
]
```

---

# 49. Keep HTTP Logic Outside React Components

Create:

```text
frontend/src/api.js
```

```javascript
const API_URL =
    "http://localhost:8000/api";
```

This module will contain all communication with the backend.

Architecture:

```text
React Component
      │
      ▼
    api.js
      │
      ▼
   FastAPI
```

---

# 50. A Helper for HTTP Errors

Add:

```javascript
async function handleResponse(response) {

    if (response.ok) {
        return response.json();
    }

    let message =
        `HTTP ${response.status}`;

    try {

        const data =
            await response.json();

        message =
            data.detail ?? message;

    } catch {
        // Response was not JSON.
    }

    throw new Error(message);
}
```

Now all API functions can use the same error handling.

---

# 51. Load Documents

```javascript
export async function getDocuments() {

    const response = await fetch(
        `${API_URL}/documents`
    );

    return handleResponse(
        response
    );
}
```

---

# 52. Ask a Question

```javascript
export async function askQuestion(
    question
) {

    const response = await fetch(
        `${API_URL}/ask`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify({
                question,
            }),
        }
    );

    return handleResponse(
        response
    );
}
```

The frontend sends JSON because `/api/ask` accepts a normal request body.

---

# 53. Upload a File

```javascript
export async function uploadDocument(
    file
) {

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    const response = await fetch(
        `${API_URL}/documents`,
        {
            method: "POST",
            body: formData,
        }
    );

    return handleResponse(
        response
    );
}
```

Notice that we do **not** manually write:

```javascript
"Content-Type": "multipart/form-data"
```

When sending `FormData`, the browser creates the correct multipart content type including its boundary.

FastAPI receives uploaded files as multipart form data.

---

# 54. Delete a Document

```javascript
export async function deleteDocument(
    filename
) {

    const response = await fetch(
        `${API_URL}/documents/` +
        encodeURIComponent(filename),
        {
            method: "DELETE",
        }
    );

    return handleResponse(
        response
    );
}
```

---

# 55. Complete `api.js`

```javascript
const API_URL =
    "http://localhost:8000/api";


async function handleResponse(response) {

    if (response.ok) {
        return response.json();
    }

    let message =
        `HTTP ${response.status}`;

    try {

        const data =
            await response.json();

        message =
            data.detail ?? message;

    } catch {
        // Response was not JSON.
    }

    throw new Error(message);
}


export async function getDocuments() {

    const response = await fetch(
        `${API_URL}/documents`
    );

    return handleResponse(response);
}


export async function uploadDocument(
    file
) {

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    const response = await fetch(
        `${API_URL}/documents`,
        {
            method: "POST",
            body: formData,
        }
    );

    return handleResponse(response);
}


export async function deleteDocument(
    filename
) {

    const response = await fetch(
        `${API_URL}/documents/` +
        encodeURIComponent(filename),
        {
            method: "DELETE",
        }
    );

    return handleResponse(response);
}


export async function askQuestion(
    question
) {

    const response = await fetch(
        `${API_URL}/ask`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify({
                question,
            }),
        }
    );

    return handleResponse(response);
}
```

---

# 56. Build the React Component

Replace:

```text
frontend/src/App.jsx
```

with:

```jsx
import {
    useEffect,
    useState,
} from "react";

import {
    askQuestion,
    deleteDocument,
    getDocuments,
    uploadDocument,
} from "./api";


export default function App() {

    const [
        documents,
        setDocuments,
    ] = useState([]);

    const [
        selectedFile,
        setSelectedFile,
    ] = useState(null);

    const [
        question,
        setQuestion,
    ] = useState("");

    const [
        answer,
        setAnswer,
    ] = useState("");

    const [
        sources,
        setSources,
    ] = useState([]);

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");


    async function refreshDocuments() {

        const data =
            await getDocuments();

        setDocuments(data);
    }


    useEffect(() => {

        refreshDocuments()
            .catch(error => {
                setError(
                    error.message
                );
            });

    }, []);


    async function handleUpload(event) {

        event.preventDefault();

        if (!selectedFile) {
            return;
        }

        setLoading(true);
        setError("");

        try {

            await uploadDocument(
                selectedFile
            );

            setSelectedFile(null);

            await refreshDocuments();

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setLoading(false);
        }
    }


    async function handleDelete(filename) {

        setLoading(true);
        setError("");

        try {

            await deleteDocument(
                filename
            );

            await refreshDocuments();

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setLoading(false);
        }
    }


    async function handleAsk(event) {

        event.preventDefault();

        const value =
            question.trim();

        if (!value) {
            return;
        }

        setLoading(true);
        setError("");

        try {

            const result =
                await askQuestion(
                    value
                );

            setAnswer(
                result.answer
            );

            setSources(
                result.sources
            );

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setLoading(false);
        }
    }


    return (
        <main className="container">

            <h1>
                BluePeak Knowledge Assistant
            </h1>


            <section>

                <h2>
                    Knowledge Base
                </h2>

                <form
                    onSubmit={handleUpload}
                >

                    <input
                        type="file"
                        accept=".md,.txt"

                        onChange={event => {
                            setSelectedFile(
                                event
                                    .target
                                    .files[0]
                                    ?? null
                            );
                        }}
                    />

                    <button
                        disabled={
                            loading
                            || !selectedFile
                        }
                    >
                        Upload
                    </button>

                </form>


                <ul>

                    {documents.map(
                        document => (

                            <li
                                key={
                                    document.name
                                }
                            >

                                <span>
                                    {document.name}
                                </span>

                                <button
                                    disabled={
                                        loading
                                    }

                                    onClick={() =>
                                        handleDelete(
                                            document.name
                                        )
                                    }
                                >
                                    Delete
                                </button>

                            </li>
                        )
                    )}

                </ul>

            </section>


            <section>

                <h2>
                    Ask a Question
                </h2>

                <form
                    onSubmit={handleAsk}
                >

                    <textarea
                        value={question}

                        onChange={event =>
                            setQuestion(
                                event.target.value
                            )
                        }

                        rows="4"

                        placeholder={
                            "Ask about company policies..."
                        }
                    />

                    <button
                        disabled={loading}
                    >
                        Ask
                    </button>

                </form>

            </section>


            {loading && (
                <p>
                    Processing...
                </p>
            )}


            {error && (
                <p className="error">
                    {error}
                </p>
            )}


            {answer && (

                <section>

                    <h2>
                        Answer
                    </h2>

                    <p>
                        {answer}
                    </p>


                    <h3>
                        Sources
                    </h3>

                    <ul>

                        {sources.map(
                            (
                                source,
                                index
                            ) => (

                                <li key={index}>

                                    {
                                        source.source
                                    }

                                    {
                                        source.start_index
                                        !== null
                                        &&
                                        ` — position ${source.start_index}`
                                    }

                                </li>
                            )
                        )}

                    </ul>

                </section>
            )}

        </main>
    );
}
```

---

# 57. Why `useEffect()`?

We want to load the current document list when the component appears.

```jsx
useEffect(() => {

    refreshDocuments();

}, []);
```

React describes Effects as a mechanism for synchronizing a component with an external system; fetching external data is one supported use case.

Here the external system is:

```text
FastAPI backend
```

---

# 58. Why We Do Not Use Redux

Students already know Redux, but this application does not need global state management yet.

Current state is small:

```text
documents
selectedFile
question
answer
sources
loading
error
```

Using:

```text
useState
```

is sufficient.

If the application later grows into:

```text
authentication
multiple conversations
user settings
document collections
cached server state
```

then a larger state/data-management solution may become useful.

Do not add complexity simply because a tool exists.

---

# 59. Minimal CSS

Replace:

```text
frontend/src/index.css
```

with:

```css
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family:
        system-ui,
        sans-serif;
    background: #f5f5f5;
}

button,
input,
textarea {
    font: inherit;
}

button {
    cursor: pointer;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 32px 20px;
}

section {
    background: white;
    margin: 24px 0;
    padding: 24px;
    border-radius: 8px;
}

form {
    display: grid;
    gap: 12px;
}

textarea {
    width: 100%;
    padding: 12px;
}

ul {
    padding-left: 20px;
}

li {
    margin: 8px 0;
}

.error {
    color: #b00020;
}
```

The visual design is intentionally simple.

The goal is the full-stack RAG architecture.

---

# 60. Run the Complete System

You now need three processes.

## Terminal 1 — PostgreSQL

```bash
docker compose up -d
```

---

## Terminal 2 — FastAPI

```bash
cd backend
```

```bash
source .venv/bin/activate
```

```bash
uvicorn app.main:app --reload
```

---

## Terminal 3 — React

```bash
cd frontend
```

```bash
npm run dev
```

Ollama must also be running on the machine.

---

# 61. Complete Runtime Architecture

```text
Browser
http://localhost:5173
        │
        │ HTTP
        ▼
FastAPI
http://localhost:8000
        │
        ├──────────────► knowledge/*.md
        │
        ├──────────────► Ollama
        │                 │
        │                 ├── embeddinggemma
        │                 └── gemma3:4b
        │
        └──────────────► PostgreSQL
                          │
                          └── pgvector
```

---

# 62. Test the Complete Application

Open the frontend.

Ask:

```text
How many vacation days do employees receive?
```

Expected result:

```text
24 working days
```

with:

```text
employee_handbook.md
```

as a source.

---

# 63. Upload a New Document

Create:

```text
office_policy.md
```

For example:

```markdown
# Office Policy

## Opening Hours

The main office is open from 7:00 AM
until 9:00 PM Monday through Friday.

## Parking

Employees may use the underground parking
garage after registering their vehicle with
the facilities team.

## Guests

Visitors must be registered with reception
before entering the office area.
```

Upload it through React.

The backend performs:

```text
Upload
 ↓
Save
 ↓
Rebuild Index
```

---

# 64. Ask About the New Document

Ask:

```text
Can visitors enter the office without registration?
```

The RAG system should now retrieve:

```text
Visitors must be registered with reception...
```

The key point is:

> We changed the knowledge base without changing the LLM.

---

# 65. Delete the Document

Delete:

```text
office_policy.md
```

from the browser.

Then ask again:

```text
Can visitors enter the office without registration?
```

The information is no longer in the knowledge base.

A correctly grounded system should now say that the provided documents do not contain enough information.

---

# 66. This Demonstrates a Major Advantage of RAG

The knowledge base can change:

```text
Document Added
Document Updated
Document Deleted
```

without:

```text
retraining the LLM
```

Instead:

```text
Knowledge Changes
      ↓
Re-index
      ↓
New Retrieval Behaviour
```

The generation model remains unchanged.

---

# 67. Understand the Upload Cost

Our current upload performs:

```text
1 new file
    ↓
re-embed every file
```

Suppose we have:

```text
10 documents
```

This is fine.

Suppose we have:

```text
1,000,000 chunks
```

This would be unacceptable.

---

# 68. How Production Incremental Indexing Would Work

Instead:

```text
Upload Document
      ↓
Create document_id
      ↓
Split only new document
      ↓
Create embeddings
      ↓
add_documents()
```

Each chunk should have stable metadata such as:

```python
{
    "document_id": "...",
    "source": "...",
    "chunk_index": 5,
}
```

When deleting:

```text
document_id
    ↓
find/delete its chunks
```

LangChain's vector-store abstraction includes both `add_documents` and `delete`, allowing applications to implement this lifecycle without rebuilding every vector.

We intentionally postpone this optimization.

---

# 69. Documents Need Their Own Identity

A production system should not identify a document only by:

```text
filename
```

Two users can upload:

```text
policy.md
```

Therefore a better model is:

```text
document_id
owner_id
original_filename
created_at
status
```

For example:

```text
document_id:
7ac8...

original_filename:
policy.md
```

The vector chunks then contain:

```text
document_id = 7ac8...
```

as metadata.

---

# 70. File Storage Is Also a Separate Concern

Our classroom application stores documents in:

```text
backend/knowledge/
```

A production system could instead use:

```text
Object Storage
Database
S3-compatible storage
Azure Blob Storage
Google Cloud Storage
```

The vector database does not need to be the canonical storage location for the original uploaded file.

A useful architecture is:

```text
Original Document
      ↓
File Storage

Extracted Chunks
      ↓
Vector Store
```

---

# 71. Do Not Expose Ollama Directly to the Browser

Our architecture is:

```text
Browser
  ↓
FastAPI
  ↓
Ollama
```

not:

```text
Browser
  ↓
Ollama
```

The backend is responsible for:

* authorization;
* retrieval;
* prompt construction;
* business rules;
* source handling;
* model configuration.

The frontend should call the application API rather than knowing how the RAG internals work.

---

# 72. RAG Security Boundary

Suppose the application later supports different companies:

```text
Company A
Company B
```

A user from Company A must never retrieve Company B's chunks.

Do **not** rely on semantic similarity for isolation.

You need metadata constraints such as:

```text
tenant_id = current tenant
```

combined with vector retrieval.

Conceptually:

```text
Authorization Filter
        +
Semantic Search
```

The PGVector integration supports metadata filtering, which can be used as one part of such a design.

---

# 73. File Upload Security Is a Real Topic

Our example validates:

```text
extension
size
UTF-8
filename
```

A production document-upload system may additionally need:

```text
authentication
authorization
malware scanning
content validation
storage quotas
rate limiting
document ownership
audit logs
```

The code in this lesson is a teaching application, not a complete secure file-upload platform.

---

# 74. Error Handling

Try uploading:

```text
photo.jpg
```

Expected:

```text
400
Only .md and .txt files are supported.
```

Try asking an empty question.

Pydantic validation should reject it because:

```python
min_length=1
```

Try deleting a missing document.

Expected:

```text
404
Document not found.
```

The frontend converts these HTTP errors into a visible message.

---

# 75. Network Debugging

If React cannot reach FastAPI:

Check:

```text
1. Is FastAPI running?
2. Is the URL correct?
3. Is CORS configured?
4. Does GET /api/health work?
5. Does /docs work?
6. Is the browser console showing an error?
```

Always test the API independently before debugging the RAG model.

---

# 76. RAG Debugging Still Has Two Layers

Even with the web application, wrong answers still fall into the same categories from Lesson 2.

## Retrieval Failure

```text
Question
 ↓
Wrong chunks
 ↓
LLM
```

## Generation Failure

```text
Question
 ↓
Correct chunks
 ↓
Wrong answer
```

Adding React and FastAPI does not change this fundamental debugging model.

---

# 77. Now There Is a Third Failure Layer

The full-stack application introduces:

```text
Application / Integration Failure
```

For example:

```text
React request never reaches FastAPI
```

or:

```text
FastAPI rejects upload
```

or:

```text
PostgreSQL is unavailable
```

So debugging now becomes:

```text
UI / HTTP
   ↓
Retrieval
   ↓
Generation
```

---

# 78. A Useful Debugging Order

If the application fails:

### Step 1 — Infrastructure

```text
Is PostgreSQL running?
Is Ollama running?
Is FastAPI running?
```

### Step 2 — API

```text
Does /api/health work?
Does /api/documents work?
```

### Step 3 — Retrieval

```text
What chunks were retrieved?
```

### Step 4 — Generation

```text
Was the correct context given to the LLM?
```

### Step 5 — Frontend

```text
Did React render the response correctly?
```

---

# 79. Local Ollama vs Ollama Cloud

So far:

```text
FastAPI
   ↓
Local Ollama
   ↓
gemma3:4b
```

The computer performs model inference locally.

Ollama also supports cloud models that can be invoked while continuing to use local Ollama tools. Ollama documents cloud models as being offloaded to its cloud service while keeping the same local workflow.

---

# 80. Sign In to Ollama

For cloud models:

```bash
ollama signin
```

Ollama then handles authentication for cloud-model requests made through the local Ollama installation.

---

# 81. Try a Cloud Model

For example:

```bash
ollama pull gpt-oss:120b-cloud
```

Then:

```bash
ollama run gpt-oss:120b-cloud
```

This model is executed in Ollama's cloud rather than requiring the local machine to hold and execute a 120B model.

---

# 82. Switch the RAG Generation Model

Change:

```python
CHAT_MODEL = "gemma3:4b"
```

to:

```python
CHAT_MODEL = (
    "gpt-oss:120b-cloud"
)
```

Restart FastAPI.

The application architecture remains:

```text
React
 ↓
FastAPI
 ↓
ChatOllama
```

but generation changes from:

```text
Local Model
```

to:

```text
Cloud Model
```

The retrieval pipeline does not need to change.

---

# 83. Keep Embeddings Local

We can still use:

```text
embeddinggemma
```

locally while using a cloud LLM for generation.

Therefore:

```text
INDEXING / RETRIEVAL

EmbeddingGemma
      ↓
Local Ollama
```

while:

```text
GENERATION

Cloud LLM
   ↓
Ollama Cloud
```

This illustrates an important principle:

> The embedding model and the generation model are independent components.

---

# 84. Architecture with Cloud Generation

```text
                         Browser
                            │
                            ▼
                         FastAPI
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
       Local Embeddings            Cloud LLM
        EmbeddingGemma          gpt-oss:120b-cloud
               │                         │
               ▼                         ▼
           pgvector                Ollama Cloud
```

The RAG architecture remains the same.

Only a provider/model boundary changed.

---

# 85. Direct Ollama Cloud API

Ollama also exposes its cloud API directly at:

```text
https://ollama.com/api
```

while the default local API is served at:

```text
http://localhost:11434/api
```

Direct cloud API access requires authentication, such as an API key.

For this lesson we use the simpler:

```text
ollama signin
+
local Ollama client
+
cloud model
```

workflow.

---

# 86. What We Have Built

We started the course section with:

```text
Text
 ↓
Vector
```

Now we have:

```text
                         USER

                          │
                          ▼

                       React UI

                          │
                          ▼

                       FastAPI

             ┌────────────┴─────────────┐
             │                          │
             ▼                          ▼

      Document Management             RAG

             │                          │
             ▼                          ▼

      Markdown / TXT              Retriever
                                      │
                                      ▼
                                  PGVector
                                      │
                                      ▼
                                   Context
                                      │
                                      ▼
                                     LLM
                                      │
                                      ▼
                                   Answer
```

This is a real application architecture rather than a standalone AI demo.

---

# 87. What Makes the Application Useful?

It supports a practical workflow:

```text
1. Add internal information.
2. Index it.
3. Ask natural-language questions.
4. Retrieve relevant evidence.
5. Generate an answer.
6. Show its sources.
7. Update the knowledge base without retraining.
```

The same architecture can be adapted to:

* company documentation;
* technical documentation;
* university regulations;
* product support;
* legal document search;
* internal procedures;
* course materials;
* customer FAQs.

---

# 88. In-Class Exercise

Add another knowledge area:

```text
Product Support
```

Create:

```text
product_support.md
```

containing at least four sections:

```text
Installation
System Requirements
Troubleshooting
Refund Policy
```

Upload the file through the React UI.

Then test at least five questions.

For each question record:

```text
Question
Retrieved Source
Answer
```

At least one question should use wording very different from the source text.

---

# 89. In-Class Exercise — Unknown Information

Ask at least two questions whose answers do not exist in the uploaded documents.

Verify that the assistant does not simply invent a policy.

Then add a document containing one of the missing answers, re-index through upload, and ask the same question again.

Observe:

```text
Before upload
   ↓
Unknown

After upload
   ↓
Answerable
```

No model training occurred.

---

# 90. In-Class Exercise — Delete

Delete the document again.

Ask the same question.

The system should return to:

```text
Unknown
```

This demonstrates that RAG knowledge is controlled by the external knowledge base.

---

# 91. In-Class Exercise — Inspect Network Requests

Open browser developer tools.

Inspect:

```text
POST /api/ask
```

Request:

```json
{
  "question": "..."
}
```

Response:

```json
{
  "answer": "...",
  "sources": [...]
}
```

Also inspect:

```text
POST /api/documents
```

Notice that it uses:

```text
multipart/form-data
```

instead of JSON because a file is being uploaded. FastAPI's documentation distinguishes multipart file/form requests from ordinary JSON request bodies.

---

# 92. Homework

## Extend the Full-Stack RAG Application

Extend the application created during the lesson.

---

## Requirement 1 — Multiple Knowledge Categories

Every uploaded document should have a category.

For example:

```text
HR
Security
Travel
Technical
```

The frontend should allow the user to select a category during upload.

Store the category in chunk metadata.

---

## Requirement 2 — Category Filtering

Add an optional category field to a question.

Example:

```json
{
  "question": "What is the access policy?",
  "category": "Security"
}
```

When category is present, retrieval should search only chunks with matching metadata.

---

## Requirement 3 — Better Document Identity

Do not use only the filename as the document identity.

Generate:

```text
document_id
```

for each uploaded document.

For example:

```python
from uuid import uuid4

document_id = str(
    uuid4()
)
```

Store it in chunk metadata:

```python
{
    "document_id": document_id,
    "source": filename,
    "category": category,
}
```

---

## Requirement 4 — Incremental Indexing

Replace:

```text
rebuild entire collection
```

with:

```text
upload
 ↓
index only new document
```

The vector store's `add_documents()` operation can add new documents without rebuilding the whole collection.

---

## Requirement 5 — Incremental Delete

When a document is deleted:

```text
document_id
 ↓
delete its vectors
 ↓
delete original document
```

Do not regenerate embeddings for unrelated documents.

---

## Requirement 6 — UI Status

Show separate states:

```text
Uploading...
Indexing...
Asking...
Deleting...
```

Disable relevant buttons while an operation is running.

---

## Requirement 7 — Error Handling

Display useful errors for:

```text
unsupported file type
file too large
backend unavailable
empty question
document not found
```

---

## Requirement 8 — Test Questions

Create at least:

```text
10 answerable questions
```

and:

```text
5 unanswerable questions
```

Record:

```text
question
expected source
actual source
answer
```

---

# 93. Optional Advanced Task — RTK Query

The current frontend uses:

```text
fetch()
```

directly.

As an optional task, replace the API layer with Redux Toolkit Query.

Create operations for:

```text
getDocuments
uploadDocument
deleteDocument
askQuestion
```

This is useful practice because the frontend already has a clear REST API boundary.

---

# 94. Optional Advanced Task — Conversation UI

Change the single answer UI into:

```text
User
Assistant
User
Assistant
```

But remember:

> Rendering messages as a conversation does not automatically create conversational RAG.

To correctly support follow-up questions such as:

```text
And what about domestic travel?
```

the backend must also take conversation context into account.

---

# 95. Optional Advanced Task — Cloud Generation

Switch:

```python
CHAT_MODEL = "gemma3:4b"
```

to an available Ollama cloud model after signing in.

Compare:

```text
response quality
latency
local hardware usage
```

Ollama cloud models are designed to let local Ollama workflows use models that are executed remotely.

---

# 96. What We Have Not Solved Yet

Our application is useful, but it is not production-ready.

Important future topics include:

```text
authentication
authorization
multi-tenancy
incremental indexing
document versioning
PDF parsing
structured documents
hybrid search
reranking
retrieval evaluation
RAG evaluation
streaming answers
conversation history
observability
background indexing
deployment
```

These are natural topics for an **Advanced RAG** module.

---

# 97. The Three-Lesson Progression

## Lesson 1

```text
What is semantic retrieval?
```

We built:

```text
Embeddings
+
Vector Search
```

---

## Lesson 2

```text
How does RAG answer questions?
```

We built:

```text
Retrieval
+
Context
+
LLM
```

---

## Lesson 3

```text
How do we turn RAG into an application?
```

We built:

```text
React
+
FastAPI
+
RAG
+
Document Management
```

---

# 98. Final Architecture

```text
┌───────────────────────────────────────────────────────┐
│                       React                           │
│                                                       │
│ Upload Documents                                      │
│ Ask Questions                                         │
│ Display Answers                                       │
│ Display Sources                                       │
└─────────────────────────┬─────────────────────────────┘
                          │
                          │ HTTP
                          ▼
┌───────────────────────────────────────────────────────┐
│                      FastAPI                          │
│                                                       │
│ GET    /api/documents                                 │
│ POST   /api/documents                                 │
│ DELETE /api/documents/{filename}                      │
│ POST   /api/ask                                       │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│                     RAG Service                       │
│                                                       │
│ Load → Split → Embed → Store                          │
│                                                       │
│ Question → Retrieve → Prompt → Generate               │
└──────────────┬──────────────────────────┬─────────────┘
               │                          │
               ▼                          ▼
┌───────────────────────────┐   ┌───────────────────────┐
│          Ollama           │   │ PostgreSQL + pgvector │
│                           │   │                       │
│ embeddinggemma            │   │ chunks                │
│ gemma3:4b / cloud model   │   │ embeddings            │
└───────────────────────────┘   │ metadata              │
                                └───────────────────────┘
```

---

# 99. Final Mental Model

A RAG application is not:

```text
LLM + Documents
```

It is a system containing several independent components:

```text
Document Storage
      │
      ▼
Text Processing
      │
      ▼
Embeddings
      │
      ▼
Vector Store
      │
      ▼
Retriever
      │
      ▼
Prompt Construction
      │
      ▼
LLM
      │
      ▼
Application API
      │
      ▼
User Interface
```

Each layer has a different responsibility.

---

# 100. The Most Important Principle

```text
The vector store stores and retrieves knowledge.

The retriever finds relevant evidence.

The prompt supplies that evidence to the model.

The LLM generates the answer.

FastAPI exposes the capability.

React provides the user interface.
```

Understanding these boundaries makes it possible to replace individual components without redesigning the entire application.

For example:

```text
PostgreSQL
    ↓
another Vector Store
```

or:

```text
Local Ollama
    ↓
Ollama Cloud
```

or:

```text
React
    ↓
another client
```

while the fundamental RAG architecture remains the same.

---

# References

* FastAPI — Request Files.
* FastAPI — `UploadFile`.
* FastAPI — CORS.
* FastAPI — Request Forms and Files.
* LangChain — PGVector integration.
* LangChain — Vector Store interface.
* LangChain — Ollama embeddings.
* LangChain — ChatOllama.
* Vite — Getting Started.
* React — `useEffect`.
* Ollama — Cloud Models.
* Ollama — API Authentication.
* Ollama — API Introduction.

