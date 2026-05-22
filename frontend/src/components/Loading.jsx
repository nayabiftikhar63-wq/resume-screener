export default function Loading({ active, message = 'Processing…' }) {
  if (!active) return null;
  return (
    <div className="loading-overlay active">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  );
}
