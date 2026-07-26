function ArchitectureView({ readme }) {
  if (!readme) return null;

  return (
    <div className="panel panel--overview">
      <p className="panel-title"><span className="dot" /> Architecture overview</p>
      <div className="code-block">{readme}</div>
    </div>
  );
}

export default ArchitectureView;