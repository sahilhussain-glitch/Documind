import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export function QueryInterface({ documents, setResult }) {
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState("ask"); // ask | summarize | extract | classify
  const [fields, setFields] = useState("date, parties, amount");
  const [categories, setCategories] = useState("invoice, contract, report, email");
  const [selectedDoc, setSelectedDoc] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setLoading(true);
    try {
      let res;
      if (mode === "ask") {
        res = await axios.post(`${API}/api/query/ask`, {
          question,
          doc_ids: selectedDoc ? [selectedDoc] : null,
        });
        setResult({ type: "qa", data: res.data });
      } else if (mode === "summarize") {
        res = await axios.post(`${API}/api/query/summarize`, { doc_id: selectedDoc, style: "bullets" });
        setResult({ type: "summary", data: res.data });
      } else if (mode === "extract") {
        res = await axios.post(`${API}/api/query/extract`, {
          doc_id: selectedDoc,
          fields: fields.split(",").map(f => f.trim()),
        });
        setResult({ type: "extract", data: res.data });
      } else if (mode === "classify") {
        res = await axios.post(`${API}/api/query/classify`, {
          doc_id: selectedDoc,
          categories: categories.split(",").map(c => c.trim()),
        });
        setResult({ type: "classify", data: res.data });
      }
    } catch (err) {
      setResult({ type: "error", data: { message: err.response?.data?.detail || err.message } });
    }
    setLoading(false);
  }

  return (
    <div>
      <h2 style={{ color: "#1E1E2E" }}>Query Documents</h2>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        {["ask", "summarize", "extract", "classify"].map(m => (
          <button key={m} onClick={() => setMode(m)}
            style={{
              padding: "0.4rem 1rem", border: "none", borderRadius: 6, cursor: "pointer",
              background: mode === m ? "#1A56DB" : "#f0f4ff",
              color: mode === m ? "#fff" : "#1A56DB", fontWeight: 600,
            }}>{m}</button>
        ))}
      </div>

      {documents.length > 0 && (
        <select value={selectedDoc} onChange={e => setSelectedDoc(e.target.value)}
          style={{ width: "100%", padding: "0.6rem", marginBottom: "1rem", borderRadius: 6, border: "1px solid #cbd5e1" }}>
          <option value="">All documents</option>
          {documents.map(d => <option key={d.doc_id} value={d.doc_id}>{d.filename}</option>)}
        </select>
      )}

      {mode === "ask" && (
        <textarea value={question} onChange={e => setQuestion(e.target.value)}
          placeholder="Ask a question about your documents..."
          style={{ width: "100%", height: 100, padding: "0.75rem", borderRadius: 8,
            border: "1px solid #cbd5e1", fontSize: 15, resize: "vertical", boxSizing: "border-box" }} />
      )}
      {mode === "extract" && (
        <input value={fields} onChange={e => setFields(e.target.value)}
          placeholder="Fields: date, parties, amount"
          style={{ width: "100%", padding: "0.6rem", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }} />
      )}
      {mode === "classify" && (
        <input value={categories} onChange={e => setCategories(e.target.value)}
          placeholder="Categories: invoice, contract, report"
          style={{ width: "100%", padding: "0.6rem", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }} />
      )}

      <button onClick={handleSubmit} disabled={loading}
        style={{
          marginTop: "1rem", padding: "0.75rem 2rem", background: "#1A56DB", color: "#fff",
          border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 700, fontSize: 15
        }}>
        {loading ? "Processing..." : "Run"}
      </button>
    </div>
  );
}

export default QueryInterface;
