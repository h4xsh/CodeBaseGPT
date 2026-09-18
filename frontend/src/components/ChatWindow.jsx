import { useState } from "react";
import ChatMessage from "./ChatMessage";

export default function ChatWindow({ repositoryId, messages, onSend, loading, error }) {
  const [question, setQuestion] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    if (!question.trim() || loading) return;
    onSend(question.trim());
    setQuestion("");
  }

  return (
    <section className="panel chat-panel">
      <div className="panel-heading">
        <span>Ask about the code</span>
        {repositoryId && <span className="status-indicator"><span className="status-dot" /> Indexed</span>}
      </div>
      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <h2>Explore your repository</h2>
            <p>Ask how a feature works, where code lives, or how files connect.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage key={`${message.role}-${index}`} message={message} />
          ))
        )}
        {loading && <div className="typing">Searching the repository and thinking...</div>}
      </div>
      {error && <p className="error-text chat-error">{error}</p>}
      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={repositoryId ? "How does authentication work?" : "Analyze a repository first"}
          disabled={!repositoryId || loading}
          rows={2}
        />
        <button type="submit" disabled={!repositoryId || loading || !question.trim()}>
          {loading ? "..." : "Send"}
        </button>
      </form>
    </section>
  );
}
