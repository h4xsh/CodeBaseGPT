import SourceCard from "./SourceCard";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`chat-message ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-label">
        {isUser ? "You" : `CodebaseGPT${message.model ? ` · ${message.model}` : ""}`}
      </div>
      <div className="message-content">
        {isUser ? message.content : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ children }) => (
                <div className="markdown-table">
                  <table>{children}</table>
                </div>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
      {!isUser && message.sources?.length > 0 && (
        <div className="sources">
          <div className="sources-heading">Sources</div>
          {message.sources.map((source) => (
            <SourceCard
              key={`${source.file_path}-${source.chunk_index}`}
              source={source}
            />
          ))}
        </div>
      )}
    </article>
  );
}
