export default function SourceCard({ source }) {
  return (
    <article className="source-card">
      <div className="source-header">
        <strong>{source.file_path}</strong>
        <span>chunk {source.chunk_index}</span>
      </div>
      <pre>{source.snippet}</pre>
    </article>
  );
}
