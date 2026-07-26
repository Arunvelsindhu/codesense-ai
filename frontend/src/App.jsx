import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import SnippetExplainer from "./components/SnippetExplainer";

function App() {
  const [mode, setMode] = useState("repo");

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "center", gap: 10, paddingTop: 24 }}>
        <button
          className={mode === "repo" ? "btn-primary" : "btn-secondary"}
          onClick={() => setMode("repo")}
        >
          Analyze a repo
        </button>
        <button
          className={mode === "snippet" ? "btn-primary" : "btn-secondary"}
          onClick={() => setMode("snippet")}
        >
          Explain a snippet
        </button>
      </div>

      {mode === "repo" ? (
        <Dashboard />
      ) : (
        <div className="app-shell">
          <div className="results-wrap">
            <SnippetExplainer />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;