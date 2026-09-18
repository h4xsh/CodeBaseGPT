import { useState } from "react";

export default function RepositoryInput({ onSubmit, loading, error }) {
  const [url, setUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(url.trim());
  }

  return (
    <form className="repository-form" onSubmit={handleSubmit}>
      <label htmlFor="github-url">Public GitHub repository</label>
      <div className="repository-input-row">
        <input
          id="github-url"
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://github.com/owner/repository"
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading || !url.trim()}>
          {loading ? "Indexing..." : "Analyze repository"}
        </button>
      </div>
      {error && <p className="error-text">{error}</p>}
    </form>
  );
}
