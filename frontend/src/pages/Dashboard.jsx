import { useState, useEffect, useCallback } from "react";
import RepoUpload from "../components/RepoUpload";
import ChatWindow from "../components/ChatWindow";
import ArchitectureView from "../components/ArchitectureView";
import DocsPanel from "../components/DocsPanel";
import TestResults from "../components/TestResults";
import { listRepos, getRepo, exportRepoDocs } from "../api/apiClient";

function Dashboard() {
  const [analysis, setAnalysis] = useState(null);
  const [recentRepos, setRecentRepos] = useState([]);
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState("");
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  const refreshRepoHistory = useCallback(() => {
    listRepos()
      .then((res) => setRecentRepos(res.data.repos || []))
      .catch(() => {
        // History is a nice-to-have; a failed fetch shouldn't block the app.
      });
  }, []);

  useEffect(() => {
    refreshRepoHistory();
  }, [refreshRepoHistory]);

  const handleAnalysisComplete = (result) => {
    setAnalysis(result);
    refreshRepoHistory();
  };

  const handleSelectRecent = async (repoName) => {
    setSwitching(true);
    setSwitchError("");
    try {
      const res = await getRepo(repoName);
      setAnalysis({ repoName, ...res.data });
    } catch (err) {
      setSwitchError(err.response?.data?.detail || "Could not load that repo's cached results.");
    } finally {
      setSwitching(false);
    }
  };

  const handleExport = async () => {
    if (!analysis) return;
    setExporting(true);
    setExportError("");
    try {
      await exportRepoDocs(analysis.repoName);
    } catch (err) {
      setExportError(err.message || "Export failed.");
    } finally {
      setExporting(false);
    }
  };

  if (!analysis) {
    return (
      <RepoUpload
        onAnalysisComplete={handleAnalysisComplete}
        recentRepos={recentRepos}
        onSelectRecent={handleSelectRecent}
      />
    );
  }

  const otherRepos = recentRepos.filter((r) => r.repo_name !== analysis.repoName);

  return (
    <div className="content-pad">
      <div className="repo-banner">
        <div>
          <p className="eyebrow">Analysis complete</p>
          <h2 className="repo-title">{analysis.repoName}</h2>
        </div>
        <div className="stat-chips">
          <span className="chip chip-accent">{analysis.total_chunks} chunks</span>
          <span className="chip">{analysis.chunks_embedded} embedded</span>
        </div>
      </div>

      {switching && <p className="status-line">Loading cached results...</p>}
      {switchError && <p className="status-line error">{switchError}</p>}

      {otherRepos.length > 0 && (
        <div className="panel panel--overview">
          <p className="panel-title"><span className="dot" /> Switch repo</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {otherRepos.slice(0, 6).map((repo) => (
              <button
                key={repo.repo_name}
                className="btn-secondary"
                onClick={() => handleSelectRecent(repo.repo_name)}
                disabled={switching}
              >
                {repo.repo_name}
              </button>
            ))}
          </div>
        </div>
      )}

      <ArchitectureView readme={analysis.readme} />

      <div className="panel panel--analysis">
        <p className="panel-title"><span className="dot" /> Code analysis</p>
        <div className="code-block">{analysis.code_issues_summary}</div>
      </div>

      <div className="panel panel--export">
        <p className="panel-title"><span className="dot" /> Export</p>
        <p className="panel-desc">
          Download the architecture overview, code analysis, and evaluation metrics as a single Markdown file.
        </p>
        <button className="btn-primary" onClick={handleExport} disabled={exporting}>
          {exporting ? "Preparing download..." : "Download report"}
        </button>
        {exportError && <p className="status-line error" style={{ marginTop: 10 }}>{exportError}</p>}
      </div>

      <ChatWindow repoName={analysis.repoName} />
      <DocsPanel repoName={analysis.repoName} />
      <TestResults repoName={analysis.repoName} />

      <div className="footer-actions">
        <button className="btn-secondary" onClick={() => setAnalysis(null)}>
          Analyze another repo
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
