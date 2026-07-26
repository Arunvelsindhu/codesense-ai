import { useState } from "react";
import { queryRepo } from "../api/apiClient";

function ChatWindow({ repoName }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    const trimmed = question.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await queryRepo(repoName, trimmed);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer, sources: res.data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: err.response?.data?.detail || "Something went wrong." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) handleAsk();
  };

  return (
    <div className="panel panel--chat">
      <p className="panel-title"><span className="dot" /> Ask about this repo</p>

      <div className="chat-log">
        {messages.length === 0 && (
          <p className="chat-empty">Try: "What does this project do?" or "Explain the main function."</p>
        )}
        {messages.map((msg, idx) => (
          <div key={idx}>
            <div className={`chat-bubble ${msg.role}`}>{msg.text}</div>
            {msg.sources?.length > 0 && (
              <div className="chat-sources">
                {msg.sources.map((s) => `${s.name} · ${s.file}`).join("  ")}
              </div>
            )}
          </div>
        ))}
        {loading && <p className="chat-empty">Thinking...</p>}
      </div>

      <div className="field-row">
        <input
          className="field-input"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the code..."
          disabled={loading}
        />
        <button className="btn-primary" onClick={handleAsk} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;