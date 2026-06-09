import { useState } from "react";
import { api, isApiError, type EncodeResponse } from "../api";

export function EncodePanel() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<EncodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
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
  }

  return (
    <div className="panel">
      <h2>Encode — text → token IDs</h2>
      <label>Input text</label>
      <textarea rows={4} value={text} onChange={(e) => setText(e.target.value)} placeholder="Hello world" />
      <button className="submit" onClick={submit} disabled={loading}>
        {loading ? "Encoding…" : "Encode"}
      </button>
      {error && <div className="error-box">{error}</div>}
      {result && (
        <div className="result">
          <div style={{ marginBottom: "0.6rem" }}>
            <strong>{result.num_tokens}</strong> tokens &nbsp;·&nbsp; model: <code>{result.model}</code>
          </div>
          <div style={{ marginBottom: "0.5rem" }}>
            {result.tokens.map((tok, i) => (
              <span key={i} className="tag" title={String(result.token_ids[i])}>
                {tok}
              </span>
            ))}
          </div>
          <label style={{ marginTop: "0.5rem" }}>Token IDs</label>
          <pre>{JSON.stringify(result.token_ids)}</pre>
        </div>
      )}
    </div>
  );
}
