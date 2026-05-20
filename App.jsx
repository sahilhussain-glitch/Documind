import { useState } from "react";
import DocumentUpload from "./components/DocumentUpload";
import QueryInterface from "./components/QueryInterface";
import ResultCard from "./components/ResultCard";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("upload");

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <header style={{ marginBottom: "2rem", borderBottom: "2px solid #1A56DB", paddingBottom: "1rem" }}>
        <h1 style={{ color: "#1A56DB", margin: 0 }}>📄 DocuMind</h1>
        <p style={{ color: "#5A5A72", margin: "0.25rem 0 0" }}>LLM-Powered Document Intelligence</p>
      </header>

      <nav style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
        {["upload", "query", "extract"].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            style={{
              padding: "0.5rem 1.25rem", border: "none", borderRadius: 6, cursor: "pointer",
              background: activeTab === tab ? "#1A56DB" : "#f0f4ff",
              color: activeTab === tab ? "#fff" : "#1A56DB", fontWeight: 600,
            }}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      {activeTab === "upload" && (
        <DocumentUpload documents={documents} setDocuments={setDocuments} />
      )}
      {activeTab === "query" && (
        <QueryInterface documents={documents} setResult={setResult} />
      )}
      {result && <ResultCard result={result} />}
    </div>
  );
}
