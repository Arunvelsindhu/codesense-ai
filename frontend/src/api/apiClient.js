import axios from "axios";

export const API_BASE_URL = "http://127.0.0.1:8001/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const cloneRepo = (repoUrl, githubToken) =>
  apiClient.post("/repo/clone", {
    repo_url: repoUrl,
    ...(githubToken ? { github_token: githubToken } : {}),
  });

export const analyzeRepo = (repoName) =>
  apiClient.post("/repo/analyze", { repo_name: repoName });

export const queryRepo = (repoName, question) =>
  apiClient.post("/query", { repo_name: repoName, question });

export const getReadme = (repoName) =>
  apiClient.post("/docs/readme", { repo_name: repoName });

export const explainSnippet = (code, language = "auto") =>
  apiClient.post("/docs/explain-snippet", { code, language });

export const listRepos = () => apiClient.get("/repo/list");

export const getRepo = (repoName) =>
  apiClient.get(`/repo/${encodeURIComponent(repoName)}`);

/**
 * Streams repo analysis progress via Server-Sent Events (SSE).
 * The backend emits a "progress" event as each pipeline node completes,
 * then a "complete" event with the final result. axios doesn't handle
 * streaming bodies well in the browser, so this uses fetch directly.
 */
export async function analyzeRepoStream(repoName, { onProgress, onComplete, onError }) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/repo/analyze/stream?repo_name=${encodeURIComponent(repoName)}`
    );

    if (!response.ok || !response.body) {
      let detail = `Request failed with status ${response.status}`;
      try {
        const errJson = await response.json();
        detail = errJson.detail || detail;
      } catch {
        // ignore, keep default detail
      }
      onError(detail);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let boundary;
      while ((boundary = buffer.indexOf("\n\n")) !== -1) {
        const rawEvent = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);

        const dataLine = rawEvent.split("\n").find((l) => l.startsWith("data:"));
        if (!dataLine) continue;

        const event = JSON.parse(dataLine.slice(5).trim());

        if (event.event === "progress") onProgress(event);
        else if (event.event === "complete") onComplete(event.result);
        else if (event.event === "error") onError(event.message);
      }
    }
  } catch (err) {
    onError(err.message || "Something went wrong while streaming analysis.");
  }
}

/**
 * Downloads the export bundle (README + code analysis + eval metrics)
 * as a Markdown file, triggering the browser's native download.
 */
export async function exportRepoDocs(repoName) {
  const response = await fetch(`${API_BASE_URL}/docs/export/${encodeURIComponent(repoName)}`);

  if (!response.ok) {
    let detail = "Export failed.";
    try {
      const errJson = await response.json();
      detail = errJson.detail || detail;
    } catch {
      // ignore, keep default detail
    }
    throw new Error(detail);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : `${repoName}-codesense-report.md`;

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default apiClient;
