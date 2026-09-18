import SourceCard from "./SourceCard";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`chat-message ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-label">{isUser ? "You" : "CodebaseGPT"}</div>
      <div className="message-content">{message.content}</div>
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
