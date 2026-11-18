const API_URL = '/api';

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new Error('Backend unavailable. Check that FastAPI is running on port 8000.');
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    if (typeof data?.detail === 'string') message = data.detail;
    else if (Array.isArray(data?.detail)) {
      message = data.detail.map(item => item.msg).join('; ');
    } else if (response.status >= 500) {
      message = 'Backend unavailable. Check that FastAPI is running on port 8000.';
    }
    throw new Error(message);
  }
  return data;
}

export const getDocuments = () => request('/documents');
export const askQuestion = question => request('/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question }),
});
export function uploadDocument(file) {
  const body = new FormData();
  body.append('file', file);
  return request('/documents', { method: 'POST', body });
}
export const deleteDocument = filename => request(
  `/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' },
);
