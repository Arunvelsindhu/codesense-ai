import { useState } from "react";
import apiClient from "../api/apiClient";

function DocsPanel({ repoName }) {
  const [functionName, setFunctionName] = useState("");
  const [doc, setDoc] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGetDoc = async () => {
    const trimmed = functionName.trim();
    if (!trimmed) return;
    setLoading(true);
    setError("");
    setDoc("");

    try {
      const res = await apiClient.post(
        `/docs/function?function_name=${encodeURIComponent(trimmed)}`,
        { repo_name: repoName }
      );
      setDoc(res.data.documentation);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not generate documentation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel panel--docs">
      <p className="panel-title"><span className="dot" /> Explain a function</p>
      <div className="field-row">
        <input
          className="field-input"
          type="text"
          value={functionName}
          onChange={(e) => setFunctionName(e.target.value)}
          placeholder="Function or class name"
        />
        <button className="btn-primary" onClick={handleGetDoc} disabled={loading}>
          {loading ? "Working..." : "Explain"}
        </button>
      </div>

      {error && <p className="status-line error">{error}</p>}
      {doc && <div className="code-block" style={{ marginTop: 14 }}>{doc}</div>}
    </div>
  );
}

export default DocsPanel;