import { useMemo, useState } from "react";
import FileTree from "../components/FileTree";
import ChatWindow from "../components/ChatWindow";
import RepositoryInput from "../components/RepositoryInput";
import { askQuestion, createRepository } from "../services/api";

export default function Home() {
  const [repository, setRepository] = useState(null);
  const [conversation, setConversation] = useState([]);
  const [repositoryLoading, setRepositoryLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [repositoryError, setRepositoryError] = useState("");
  const [chatError, setChatError] = useState("");

  const sources = useMemo(
    () => conversation.flatMap((message) => message.sources || []),
    [conversation],
  );

  async function handleRepositorySubmit(url) {
    setRepositoryLoading(true);
    setRepositoryError("");
    setConversation([]);
    try {
      setRepository(await createRepository(url));
    } catch (error) {
      setRepositoryError(error.message);
    } finally {
      setRepositoryLoading(false);
    }
  }

  async function handleSend(question) {
    const history = conversation.map(({ role, content }) => ({ role, content }));
    setChatLoading(true);
    setChatError("");
    setConversation((current) => [...current, { role: "user", content: question }]);
    try {
      const result = await askQuestion(repository.repository_id, question, history);
      setConversation((current) => [
        ...current,
        { role: "assistant", content: result.answer, sources: result.sources },
      ]);
    } catch (error) {
      setChatError(error.message);
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <div className="eyebrow">LOCAL CODE INTELLIGENCE</div>
          <h1>Codebase<span>GPT</span></h1>
        </div>
        <div className="header-status"><span className="status-dot" /> Ollama connected locally</div>
      </header>

      <section className="hero">
        <p className="eyebrow">REPOSITORY EXPLORER</p>
        <h2>Understand any codebase.</h2>
        <p className="hero-copy">
          Clone a public GitHub repository, index its source, and ask grounded questions about how it works.
        </p>
        <RepositoryInput
          onSubmit={handleRepositorySubmit}
          loading={repositoryLoading}
          error={repositoryError}
        />
        {repository && (
          <div className="repository-status">
            <span className="status-dot" />
            <strong>{repository.repository_id}</strong>
            <span>{repository.message}</span>
          </div>
        )}
      </section>

      <section className="workspace">
        <FileTree sources={sources} />
        <ChatWindow
          repositoryId={repository?.repository_id}
          messages={conversation}
          onSend={handleSend}
          loading={chatLoading}
          error={chatError}
        />
      </section>
    </main>
  );
}
