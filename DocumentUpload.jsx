import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function DocumentUpload({ documents, setDocuments }) {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setMessage("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await axios.post(`${API}/api/documents/upload`, form);
      setDocuments(prev => [...prev, res.data.document]);
      setMessage(`✅ "${file.name}" indexed successfully (${res.data.document.num_chunks} chunks)`);
    } catch (err) {
      setMessage(`❌ Upload failed: ${err.response?.data?.detail || err.message}`);
    }
    setUploading(false);
  }

  async function handleDelete(doc_id, filename) {
    await axios.delete(`${API}/api/documents/${doc_id}`);
    setDocuments(prev => prev.filter(d => d.doc_id !== doc_id));
    setMessage(`🗑️ "${filename}" removed`);
  }

  return (
    <div>
      <h2 style={{ color: "#1E1E2E" }}>Upload Documents</h2>
      <label style={{
        display: "inline-block", padding: "0.75rem 1.5rem",
        background: "#1A56DB", color: "#fff", borderRadius: 8, cursor: "pointer", marginBottom: "1rem"
      }}>
        {uploading ? "Uploading..." : "Choose File (PDF / DOCX / TXT)"}
        <input type="file" accept=".pdf,.docx,.txt" onChange={handleUpload}
          style={{ display: "none" }} disabled={uploading} />
      </label>
      {message && <p style={{ color: message.startsWith("✅") ? "green" : "red" }}>{message}</p>}

      {documents.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
          <thead>
            <tr style={{ background: "#f0f4ff" }}>
              {["Filename", "Type", "Chunks", "Uploaded", ""].map(h => (
                <th key={h} style={{ padding: "0.6rem 1rem", textAlign: "left", color: "#1A56DB" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {documents.map(doc => (
              <tr key={doc.doc_id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                <td style={{ padding: "0.6rem 1rem" }}>{doc.filename}</td>
                <td style={{ padding: "0.6rem 1rem" }}>{doc.file_type.toUpperCase()}</td>
                <td style={{ padding: "0.6rem 1rem" }}>{doc.num_chunks}</td>
                <td style={{ padding: "0.6rem 1rem" }}>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                <td style={{ padding: "0.6rem 1rem" }}>
                  <button onClick={() => handleDelete(doc.doc_id, doc.filename)}
                    style={{ background: "none", border: "1px solid #ef4444", color: "#ef4444",
                      borderRadius: 4, padding: "0.2rem 0.6rem", cursor: "pointer" }}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
