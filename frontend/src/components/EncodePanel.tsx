import { useCallback, useState } from "react";
import { api, isApiError, type EncodeResponse } from "../api";

const TOKEN_PALETTES = [
  { bg: "rgba(91,94,244,0.12)",  border: "rgba(91,94,244,0.3)",  text: "#818cf8" },
  { bg: "rgba(52,211,153,0.1)",  border: "rgba(52,211,153,0.25)", text: "#34d399" },
  { bg: "rgba(251,191,36,0.1)",  border: "rgba(251,191,36,0.25)", text: "#fbbf24" },
  { bg: "rgba(248,113,113,0.1)", border: "rgba(248,113,113,0.25)", text: "#f87171" },
  { bg: "rgba(192,132,252,0.1)", border: "rgba(192,132,252,0.25)", text: "#c084fc" },
  { bg: "rgba(56,189,248,0.1)",  border: "rgba(56,189,248,0.25)", text: "#38bdf8" },
];

function tokenColor(id: number) {
  return TOKEN_PALETTES[id % TOKEN_PALETTES.length];
}

export function EncodePanel() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<EncodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const submit = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    const res = await api.encode(text);
    setLoading(false);
    if (isApiError(res)) {
      setError(res.error.message);
    } else {
      setResult(res);
    }
  }, [text]);

  function onKeyDown(e: React.KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") void submit();
  }

  function copyIds() {
    if (!result) return;
    void navigator.clipboard.writeText(JSON.stringify(result.token_ids));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <div className="panel-title">Text → Token IDs</div>
          <div className="panel-desc">Tokenize input text using the model's vocabulary</div>
        </div>
      </div>

      <div className="field">
        <label>Input text <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(⌘ Enter to run)</span></label>
        <textarea
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type something to tokenize…"
        />
      </div>

      <div className="row" style={{ marginTop: "1rem" }}>
        <button className="btn btn-primary" onClick={submit} disabled={loading || !text.trim()}>
          {loading ? <><span className="spinner" /> Encoding…</> : "Encode →"}
        </button>
        {result && (
          <span className="badge badge-muted">{result.num_tokens} token{result.num_tokens !== 1 ? "s" : ""}</span>
        )}
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
              <span className="badge badge-accent">{result.num_tokens} tokens</span>
              <span className="model-badge">{result.model}</span>
            </div>
            <div className="row" style={{ gap: "0.5rem" }}>
              {copied && <span className="copy-hint">Copied!</span>}
              <button className="btn-icon" onClick={copyIds} title="Copy token IDs">⎘</button>
            </div>
          </div>
          <div className="result-body">
            <div className="section-label">Tokens</div>
            <div className="token-grid">
              {result.tokens.map((tok, i) => {
                const c = tokenColor(result.token_ids[i]);
                return (
                  <span
                    key={i}
                    className="token-chip"
                    data-id={`id: ${result.token_ids[i]}`}
                    style={{ background: c.bg, borderColor: c.border, color: c.text }}
                  >
                    {tok === " " ? "·" : tok}
                  </span>
                );
              })}
            </div>

            <div className="ids-row">
              <div className="ids-box">
                {JSON.stringify(result.token_ids)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
