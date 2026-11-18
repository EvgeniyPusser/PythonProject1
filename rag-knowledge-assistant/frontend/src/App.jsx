import { useEffect, useRef, useState } from 'react';
import { askQuestion, deleteDocument, getDocuments, uploadDocument } from './api.js';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [operation, setOperation] = useState('Loading documents…');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const fileInput = useRef(null);
  const busy = Boolean(operation);

  useEffect(() => {
    let active = true;
    getDocuments()
      .then(data => { if (active) setDocuments(data); })
      .catch(error => { if (active) setError(error.message); })
      .finally(() => { if (active) setOperation(''); });
    return () => { active = false; };
  }, []);

  function clearFeedback() {
    setError('');
    setNotice('');
  }

  async function refresh() {
    setOperation('Loading documents…');
    clearFeedback();
    try { setDocuments(await getDocuments()); }
    catch (error) { setError(error.message); }
    finally { setOperation(''); }
  }

  async function handleUpload(event) {
    event.preventDefault();
    clearFeedback();
    if (!selectedFile) return;
    if (!/\.(md|txt)$/i.test(selectedFile.name)) {
      setError('Only .md and .txt files are supported.');
      return;
    }
    if (selectedFile.size > 1_000_000) {
      setError('File is too large. Maximum size is 1 MB.');
      return;
    }
    setOperation('Uploading and indexing…');
    setResult(null);
    try {
      const data = await uploadDocument(selectedFile);
      setSelectedFile(null);
      fileInput.current.value = '';
      setNotice(`${data.filename} indexed. ${data.documents} documents · ${data.chunks} chunks.`);
      setDocuments(await getDocuments());
    } catch (error) { setError(error.message); }
    finally { setOperation(''); }
  }

  async function handleDelete(filename) {
    clearFeedback();
    setOperation(`Deleting ${filename} and rebuilding index…`);
    setResult(null);
    try {
      await deleteDocument(filename);
      setNotice(`${filename} deleted.`);
      setDocuments(await getDocuments());
    } catch (error) { setError(error.message); }
    finally { setOperation(''); }
  }

  async function handleAsk(event) {
    event.preventDefault();
    clearFeedback();
    const value = question.trim();
    if (!value) { setError('Enter a question.'); return; }
    setOperation('Asking… Local generation can take more than a minute.');
    setResult(null);
    try { setResult({ ...await askQuestion(value), question: value }); }
    catch (error) { setError(error.message); }
    finally { setOperation(''); }
  }

  return (
    <main className="container">
      <header>
        <p className="eyebrow">BLUEPEAK SYSTEMS</p>
        <h1>Knowledge Assistant</h1>
        <p>Ask your company documents. Get answers with sources.</p>
      </header>

      <div aria-live="polite" className="feedback">
        {operation && <p className="status">{operation}</p>}
        {notice && <p className="success">{notice}</p>}
      </div>
      {error && <p role="alert" className="error">{error}</p>}

      <section aria-labelledby="knowledge-heading">
        <div className="section-heading">
          <h2 id="knowledge-heading">Knowledge Base <span className="count">{documents.length}</span></h2>
          <button className="secondary" onClick={refresh} disabled={busy}>Refresh</button>
        </div>
        <form onSubmit={handleUpload} className="upload-form">
          <label htmlFor="document">Add a document <span className="hint">MD or TXT · UTF-8 · up to 1 MB</span></label>
          <div className="upload-controls">
            <input ref={fileInput} id="document" type="file" accept=".md,.txt" disabled={busy}
              onChange={event => setSelectedFile(event.target.files?.[0] ?? null)} />
            <button disabled={busy || !selectedFile}>Upload</button>
          </div>
          <p className="hint">An upload with the same filename replaces the existing document.</p>
        </form>
        {documents.length > 0 ? (
          <ul className="documents">
            {documents.map(document => (
              <li key={document.name}>
                <div><span className="filename">{document.name}</span><span className="file-size">{(document.size / 1024).toFixed(1)} KB</span></div>
                <button className="delete" onClick={() => handleDelete(document.name)} disabled={busy}
                  aria-label={`Delete ${document.name}`}>Delete</button>
              </li>
            ))}
          </ul>
        ) : !busy && <p className="hint">No documents yet. Upload your first document above.</p>}
      </section>

      <section aria-labelledby="question-heading">
        <h2 id="question-heading">Ask a Question</h2>
        <form onSubmit={handleAsk}>
          <label htmlFor="question">What would you like to know?</label>
          <textarea id="question" rows="4" maxLength={2000} value={question} disabled={busy}
            placeholder="Do I need a receipt for a $40 taxi ride?"
            onChange={event => setQuestion(event.target.value)} />
          <div className="question-footer">
            <span className="hint">{question.length} / 2000</span>
            <button disabled={busy || !question.trim()}>Ask</button>
          </div>
        </form>
      </section>

      {result && (
        <section aria-labelledby="answer-heading" aria-live="polite">
          <h2 id="answer-heading">Answer</h2>
          <p className="asked-question">{result.question}</p>
          <p className="answer">{result.answer}</p>
          <h3>Retrieved sources</h3>
          <p className="hint">Document fragments retrieved for this question.</p>
          {result.sources.length ? <ul className="sources">
            {result.sources.map(source => (
              <li key={`${source.source}:${source.start_index}`}>
                <span>{source.source}</span>
                {source.start_index != null && <span className="hint">Character {source.start_index}</span>}
              </li>
            ))}
          </ul> : <p className="hint">No sources found.</p>}
        </section>
      )}
      <footer>Lesson 3 · React + FastAPI + RAG</footer>
    </main>
  );
}
