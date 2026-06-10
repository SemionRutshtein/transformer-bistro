import { useEffect, useState } from "react";
import { api, isApiError, type HistoryRecord } from "../api";

function endpointClass(ep: string) {
  if (ep === "encode") return "ep-encode";
  if (ep === "decode") return "ep-decode";
  return "ep-generate";
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatDateFull(iso: string) {
  return new Date(iso).toLocaleString();
}

export function HistoryPanel() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [limit, setLimit] = useState(20);

  async function load(l = limit) {
    setLoading(true);
    setError(null);
    const res = await api.history(l);
    setLoading(false);
    if (isApiError(res)) {
      setError(res.error.message);
    } else {
      setRecords(res);
    }
  }

  useEffect(() => { void load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function toggleExpand(id: string) {
    setExpanded((prev) => (prev === id ? null : id));
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <div className="panel-title">Request History</div>
          <div className="panel-desc">Recent API calls stored in PostgreSQL</div>
        </div>
        <div className="row" style={{ gap: "0.5rem" }}>
          <select
            value={limit}
            onChange={(e) => { setLimit(Number(e.target.value)); void load(Number(e.target.value)); }}
            style={{
              background: "var(--bg-input)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)",
              color: "var(--text-primary)",
              padding: "0.4rem 0.6rem",
              fontSize: "0.8rem",
              cursor: "pointer",
              outline: "none",
            }}
          >
            <option value={10}>Last 10</option>
            <option value={20}>Last 20</option>
            <option value={50}>Last 50</option>
            <option value={100}>Last 100</option>
          </select>
          <button className="btn btn-ghost" onClick={() => void load(limit)} disabled={loading}>
            {loading ? <><span className="spinner" style={{ borderTopColor: "var(--text-secondary)" }} /> Refreshing</> : "↻ Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠</span>
          {error}
        </div>
      )}

      {!loading && !error && records.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">⊞</div>
          <div className="empty-text">
            No history yet.<br />
            <span style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
              DB may be disabled, or no requests have been made.
            </span>
          </div>
        </div>
      )}

      {records.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table className="history-table">
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
                <>
                  <tr key={r.id} onClick={() => toggleExpand(r.id)} title={formatDateFull(r.created_at)}>
                    <td style={{ whiteSpace: "nowrap", color: "var(--text-secondary)", fontSize: "0.78rem" }}>
                      {formatDate(r.created_at)}
                    </td>
                    <td>
                      <span className={`endpoint-pill ${endpointClass(r.endpoint)}`}>
                        {r.endpoint}
                      </span>
                    </td>
                    <td>
                      <span className="model-badge">{r.model}</span>
                    </td>
                    <td className="latency">{r.latency_ms}ms</td>
                    <td style={{ color: "var(--text-secondary)", fontSize: "0.76rem", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {Object.entries(r.response_summary)
                        .slice(0, 3)
                        .map(([k, v]) => `${k}: ${String(v)}`)
                        .join(" · ")}
                      <span style={{ marginLeft: 4, color: "var(--text-muted)" }}>
                        {expanded === r.id ? "▲" : "▼"}
                      </span>
                    </td>
                  </tr>
                  {expanded === r.id && (
                    <tr key={`${r.id}-exp`} className="expanded-row">
                      <td colSpan={5} style={{ paddingTop: "0.25rem", paddingBottom: "0.75rem" }}>
                        <div className="grid2" style={{ gap: "0.75rem" }}>
                          <div>
                            <div className="section-label" style={{ marginBottom: "0.3rem" }}>Request</div>
                            <pre className="summary-pre">{JSON.stringify(r.request_body, null, 2)}</pre>
                          </div>
                          <div>
                            <div className="section-label" style={{ marginBottom: "0.3rem" }}>Response</div>
                            <pre className="summary-pre">{JSON.stringify(r.response_summary, null, 2)}</pre>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
