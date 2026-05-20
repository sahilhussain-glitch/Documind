export default function ResultCard({ result }) {
  if (!result) return null;
  const { type, data } = result;

  const box = { background: "#f8faff", border: "1px solid #cbd5e1",
    borderRadius: 10, padding: "1.5rem", marginTop: "2rem" };

  if (type === "error") return (
    <div style={{ ...box, borderColor: "#ef4444", background: "#fff5f5" }}>
      <strong style={{ color: "#ef4444" }}>Error:</strong> {data.message}
    </div>
  );

  if (type === "qa") return (
    <div style={box}>
      <h3 style={{ color: "#1A56DB", marginTop: 0 }}>Answer</h3>
      <p style={{ lineHeight: 1.7 }}>{data.answer}</p>
      <p style={{ fontSize: 12, color: "#5A5A72" }}>Model: {data.model_used}</p>
      {data.sources?.length > 0 && (
        <>
          <h4 style={{ color: "#1E1E2E" }}>Sources</h4>
          {data.sources.map((s, i) => (
            <div key={i} style={{ background: "#fff", border: "1px solid #e5e7eb",
              borderRadius: 6, padding: "0.75rem", marginBottom: "0.5rem", fontSize: 13 }}>
              <strong>{s.filename}</strong> · Chunk #{s.chunk_index}
              <p style={{ color: "#5A5A72", margin: "0.25rem 0 0" }}>{s.excerpt}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );

  if (type === "summary") return (
    <div style={box}>
      <h3 style={{ color: "#1A56DB", marginTop: 0 }}>Summary</h3>
      <p style={{ lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{data.summary}</p>
      <p style={{ fontSize: 12, color: "#5A5A72" }}>Model: {data.model_used}</p>
    </div>
  );

  if (type === "extract") return (
    <div style={box}>
      <h3 style={{ color: "#1A56DB", marginTop: 0 }}>Extracted Fields</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <tbody>
          {Object.entries(data.extracted).map(([k, v]) => (
            <tr key={k} style={{ borderBottom: "1px solid #e5e7eb" }}>
              <td style={{ padding: "0.5rem 1rem", fontWeight: 600, color: "#1E1E2E", width: "30%" }}>{k}</td>
              <td style={{ padding: "0.5rem 1rem", color: v ? "#1E1E2E" : "#9ca3af" }}>
                {v !== null ? String(v) : "Not found"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  if (type === "classify") return (
    <div style={box}>
      <h3 style={{ color: "#1A56DB", marginTop: 0 }}>Classification</h3>
      <p><strong>Category:</strong> {data.category}</p>
      <p><strong>Confidence:</strong> {data.confidence}</p>
      <p><strong>Reasoning:</strong> {data.reasoning}</p>
    </div>
  );

  return null;
}
