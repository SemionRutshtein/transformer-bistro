import { useEffect, useState } from "react";
import { api, isApiError, type HistoryRecord } from "../api";

export function HistoryPanel() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    const res = await api.history(20);
    setLoading(false);
    if (isApiError(res)) {
      setError(res.error.message);
    } else {
      setRecords(res);
    }
  }

  useEffect(() => { void load(); }, []);

  return (
    <div className="panel">
      <h2>History — recent requests</h2>
      <button className="submit" onClick={load} disabled={loading} style={{ marginTop: 0, marginBottom: "1rem" }}>
        {loading ? "Loading…" : "Refresh"}
      </button>
      {error && <div className="error-box">{error}</div>}
      {records.length === 0 && !loading && !error && (
        <div style={{ color: "#666", fontSize: "0.85rem" }}>
          No history yet (DB may be disabled or empty).
        </div>
      )}
      {records.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Endpoint</th>
              <th>Model</th>
              <th>Latency</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td style={{ whiteSpace: "nowrap" }}>{new Date(r.created_at).toLocaleTimeString()}</td>
                <td><span className="tag">{r.endpoint}</span></td>
                <td><code style={{ fontSize: "0.75rem" }}>{r.model}</code></td>
                <td>{r.latency_ms}ms</td>
                <td style={{ fontSize: "0.75rem", color: "#aaa" }}>
                  {JSON.stringify(r.response_summary)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
