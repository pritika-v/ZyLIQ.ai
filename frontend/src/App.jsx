import { useState } from 'react'

// Backend URL — set via VITE_API_URL at build time (see docker-compose.yml).
// Falls back to localhost for running the frontend outside Docker.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null) // { extracted_json, markdown_output, validation_json, total_score, is_valid }
  const [activeTab, setActiveTab] = useState('json')

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please choose an .rtf file first.')
      return
    }
    setError('')
    setResult(null)
    setLoading(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_URL}/api/documents/upload-and-process`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Request failed with status ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
      setActiveTab('json')
    } catch (err) {
      setError(err.message || 'Something went wrong while processing the file.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>Clinical Trial Data Extraction</h1>
        <p>Upload an RTF listing file. The pipeline extracts, validates, and self-corrects the data.</p>
      </header>

      <form className="upload-form" onSubmit={handleUpload}>
        <input
          type="file"
          accept=".rtf"
          onChange={(e) => setFile(e.target.files[0] || null)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing…' : 'Process Document'}
        </button>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {loading && (
        <div className="loading-note">
          Running extraction → validation → correction loop. This can take a minute or two.
        </div>
      )}

      {result && (
        <div className="results">
          <div className="summary-bar">
            <span><strong>Listing:</strong> {result.extracted_json?.listing_number || '—'}</span>
            <span><strong>Title:</strong> {result.extracted_json?.title || '—'}</span>
            <span><strong>Rows:</strong> {result.extracted_json?.rows?.length ?? 0}</span>
            <span><strong>Score:</strong> {result.total_score?.toFixed(2)}</span>
            <span className={result.is_valid ? 'badge badge-pass' : 'badge badge-fail'}>
              {result.is_valid ? 'VALID' : 'NEEDS REVIEW'}
            </span>
          </div>

          <div className="tabs">
            <button className={activeTab === 'json' ? 'tab active' : 'tab'} onClick={() => setActiveTab('json')}>
              JSON
            </button>
            <button className={activeTab === 'markdown' ? 'tab active' : 'tab'} onClick={() => setActiveTab('markdown')}>
              Markdown
            </button>
            <button className={activeTab === 'validation' ? 'tab active' : 'tab'} onClick={() => setActiveTab('validation')}>
              Validation
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'json' && (
              <pre className="output-block">{JSON.stringify(result.extracted_json, null, 2)}</pre>
            )}
            {activeTab === 'markdown' && (
              <pre className="output-block">{result.markdown_output}</pre>
            )}
            {activeTab === 'validation' && (
              <pre className="output-block">{JSON.stringify(result.validation_json, null, 2)}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
