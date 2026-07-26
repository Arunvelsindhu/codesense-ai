import { useState } from "react";
import apiClient from "../api/apiClient";

function TestResults({ repoName }) {
  const [functionName, setFunctionName] = useState("");
  const [testCode, setTestCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerateTest = async () => {
    const trimmed = functionName.trim();
    if (!trimmed) return;
    setLoading(true);
    setError("");
    setTestCode("");

    try {
      const res = await apiClient.post(
        `/tests/generate?function_name=${encodeURIComponent(trimmed)}`,
        { repo_name: repoName }
      );
      setTestCode(res.data.unit_test);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not generate test.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel panel--tests">
      <p className="panel-title"><span className="dot" /> Generate unit test</p>
      <div className="field-row">
        <input
          className="field-input"
          type="text"
          value={functionName}
          onChange={(e) => setFunctionName(e.target.value)}
          placeholder="Function or class name"
        />
        <button className="btn-primary" onClick={handleGenerateTest} disabled={loading}>
          {loading ? "Working..." : "Generate"}
        </button>
      </div>

      {error && <p className="status-line error">{error}</p>}
      {testCode && <div className="code-block" style={{ marginTop: 14 }}>{testCode}</div>}
    </div>
  );
}

export default TestResults;