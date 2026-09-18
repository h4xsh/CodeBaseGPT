function fileNames(sources) {
  return [...new Set(sources.map((source) => source.file_path))].sort();
}

export default function FileTree({ sources }) {
  const files = fileNames(sources);

  return (
    <aside className="panel file-tree">
      <div className="panel-heading">
        <span>Relevant files</span>
        <span className="count-badge">{files.length}</span>
      </div>
      {files.length === 0 ? (
        <p className="muted-text">Sources will appear here after a question.</p>
      ) : (
        <ul>
          {files.map((file) => (
            <li key={file}>
              <span className="file-icon">·</span>
              {file}
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
