import logging
from pathlib import Path
from threading import RLock

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_EXTENSIONS, CORS_ORIGINS, KNOWLEDGE_DIR, MAX_UPLOAD_BYTES
from .knowledge import get_knowledge_files
from .rag_service import ask_question, rebuild_index
from .schemas import AskRequest, AskResponse, DocumentInfo, IndexResponse


app = FastAPI(title="BluePeak Knowledge Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
# Single-process classroom server: don't query a collection during a rebuild.
knowledge_lock = RLock()
logger = logging.getLogger(__name__)


def safe_document_path(filename: str) -> Path:
    if not filename or Path(filename).name != filename or "\\" in filename:
        raise HTTPException(400, "Invalid filename.")
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only .md and .txt files are supported.")
    path = KNOWLEDGE_DIR / filename
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise HTTPException(400, "Invalid document.")
    return path


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/documents", response_model=list[DocumentInfo])
def list_documents():
    with knowledge_lock:
        return [DocumentInfo(name=p.name, size=p.stat().st_size) for p in get_knowledge_files()]


@app.post("/api/documents", response_model=IndexResponse)
def upload_document(file: UploadFile):
    path = safe_document_path(file.filename or "")
    raw = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File is too large.")
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "File must contain UTF-8 text.") from None

    with knowledge_lock:
        previous = path.read_bytes() if path.exists() else None
        try:
            path.write_text(content, encoding="utf-8")
            documents, chunks = rebuild_index()
        except Exception:
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(previous)
            logger.error("Document indexing failed.")
            raise HTTPException(503, "Indexing failed. Check PostgreSQL and Ollama; rebuild the index before retrying.") from None
    return IndexResponse(filename=path.name, documents=documents, chunks=chunks)


@app.delete("/api/documents/{filename}")
def delete_document(filename: str):
    path = safe_document_path(filename)
    with knowledge_lock:
        if not path.exists():
            raise HTTPException(404, "Document not found.")
        previous = path.read_bytes()
        try:
            path.unlink()
            documents, chunks = rebuild_index()
        except Exception:
            path.write_bytes(previous)
            logger.error("Document deletion/indexing failed.")
            raise HTTPException(503, "Indexing failed. Check PostgreSQL and Ollama; rebuild the index before retrying.") from None
    return {"deleted": path.name, "documents": documents, "chunks": chunks}


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest):
    with knowledge_lock:
        try:
            answer, sources = ask_question(request.question)
        except Exception:
            logger.error("RAG request failed.")
            raise HTTPException(503, "RAG unavailable. Check PostgreSQL, Ollama and the document index.") from None
    return AskResponse(answer=answer, sources=sources)
