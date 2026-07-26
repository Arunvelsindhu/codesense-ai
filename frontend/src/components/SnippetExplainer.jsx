import { useState } from "react";
import { explainSnippet } from "../api/apiClient";

function SnippetExplainer() {
  const [code, setCode] = useState("");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExplain = async () => {
    if (!code.trim()) {
      setError("Paste some code first.");
      return;
    }
    setError("");
    setLoading(true);
    setExplanation("");

    try {
      const res = await explainSnippet(code.trim());
      setExplanation(res.data.explanation);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not explain this code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <p className="panel-title"><span className="dot" /> Paste code, get an explanation</p>
      <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 14 }}>
        No repo needed — paste any code snippet directly.
      </p>

      <textarea
        className="field-input"
        style={{ width: "100%", minHeight: 160, resize: "vertical", fontFamily: "var(--font-mono)" }}
        placeholder="Paste your code here..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
        disabled={loading}
      />

      <button
        className="btn-primary"
        style={{ marginTop: 12 }}
        onClick={handleExplain}
        disabled={loading}
      >
        {loading ? "Explaining..." : "Explain code"}
      </button>

      {error && <p className="status-line error">{error}</p>}
      {explanation && (
        <div className="code-block" style={{ marginTop: 16 }}>{explanation}</div>
      )}
    </div>
  );
}

export default SnippetExplainer;