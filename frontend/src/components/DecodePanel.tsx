import { useState } from "react";
import { api, isApiError, type DecodeResponse } from "../api";

export function DecodePanel() {
  const [raw, setRaw] = useState("15496 995");
  const [result, setResult] = useState<DecodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function parseIds(s: string): number[] {
    return s
      .split(/[\s,]+/)
      .map((x) => x.trim())
      .filter(Boolean)
      .map(Number);
  }

  async function submit() {
    setLoading(true);
    setError(null);
    setResult(null);
    const ids = parseIds(raw);
    if (ids.some(isNaN)) {
      setError("All values must be integers.");
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
  }

  return (
    <div className="panel">
      <h2>Decode — token IDs → text</h2>
      <label>Token IDs (space or comma separated)</label>
      <input type="text" value={raw} onChange={(e) => setRaw(e.target.value)} />
      <button className="submit" onClick={submit} disabled={loading}>
        {loading ? "Decoding…" : "Decode"}
      </button>
      {error && <div className="error-box">{error}</div>}
      {result && (
        <div className="result">
          <strong>Decoded text:</strong>
          <pre>{result.text}</pre>
          <div style={{ marginTop: "0.5rem", color: "#888", fontSize: "0.78rem" }}>
            model: {result.model}
          </div>
        </div>
      )}
    </div>
  );
}
