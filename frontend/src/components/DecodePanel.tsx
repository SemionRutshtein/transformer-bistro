import { useCallback, useState } from "react";
import { api, isApiError, type DecodeResponse } from "../api";

export function DecodePanel() {
  const [raw, setRaw] = useState("15496 995");
  const [result, setResult] = useState<DecodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  function parseIds(s: string): number[] {
    return s
      .split(/[\s,]+/)
      .map((x) => x.trim())
      .filter(Boolean)
      .map(Number);
  }

  const submit = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    const ids = parseIds(raw);
    if (ids.some(isNaN)) {
      setError("All values must be integers.");
      setLoading(false);
      return;
    }
    if (ids.length === 0) {
      setError("Enter at least one token ID.");
      setLoading(false);
      return;
    }
    const res = await api.decode(ids);
    setLoading(false);
    if (isApiError(res)) {
      setError(res.error.message);
    } else {
      setResult(res);
    }
  }, [raw]);

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") void submit();
  }

  function copyText() {
    if (!result) return;
    void navigator.clipboard.writeText(result.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  const ids = parseIds(raw);
  const idCount = ids.filter((n) => !isNaN(n)).length;

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <div className="panel-title">Token IDs → Text</div>
          <div className="panel-desc">Decode a sequence of token IDs back to text</div>
        </div>
      </div>

      <div className="field">
        <label>Token IDs <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(space or comma separated)</span></label>
        <input
          type="text"
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="15496 995 …"
        />
      </div>

      {idCount > 0 && (
        <div style={{ marginTop: "0.4rem" }}>
          <span className="badge badge-muted">{idCount} ID{idCount !== 1 ? "s" : ""} entered</span>
        </div>
      )}

      <div className="row" style={{ marginTop: "1rem" }}>
        <button className="btn btn-primary" onClick={submit} disabled={loading || !raw.trim()}>
          {loading ? <><span className="spinner" /> Decoding…</> : "Decode ←"}
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠</span>
          {error}
        </div>
      )}

      {result && (
        <div className="result-card">
          <div className="result-header">
            <div className="result-meta">
              <span className="badge badge-green">Decoded</span>
              <span className="model-badge">{result.model}</span>
            </div>
            <div className="row" style={{ gap: "0.5rem" }}>
              {copied && <span className="copy-hint">Copied!</span>}
              <button className="btn-icon" onClick={copyText} title="Copy decoded text">⎘</button>
            </div>
          </div>
          <div className="result-body">
            <div className="section-label">Decoded text</div>
            <div className="result-text" style={{ marginTop: "0.4rem" }}>{result.text}</div>
          </div>
        </div>
      )}
    </div>
  );
}
