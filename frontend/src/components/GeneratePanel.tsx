import { useState } from "react";
import { api, isApiError, type GenerateResponse } from "../api";

export function GeneratePanel() {
  const [prompt, setPrompt] = useState("Once upon a time");
  const [maxTokens, setMaxTokens] = useState(50);
  const [temperature, setTemperature] = useState(0.8);
  const [topP, setTopP] = useState(0.95);
  const [topK, setTopK] = useState(50);
  const [doSample, setDoSample] = useState(true);
  const [seed, setSeed] = useState<string>("");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError(null);
    setResult(null);
    const res = await api.generate({
      prompt,
      max_new_tokens: maxTokens,
      temperature,
      top_p: topP,
      top_k: topK,
      do_sample: doSample,
      seed: seed !== "" ? parseInt(seed) : null,
    });
    setLoading(false);
    if (isApiError(res)) {
      setError(res.error.message);
    } else {
      setResult(res);
    }
  }

  return (
    <div className="panel">
      <h2>Generate — prompt → text</h2>
      <label>Prompt</label>
      <textarea rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} />

      <div className="grid2">
        <div>
          <label>Max new tokens ({maxTokens})</label>
          <input type="number" min={1} max={512} value={maxTokens}
            onChange={(e) => setMaxTokens(Number(e.target.value))} />
        </div>
        <div>
          <label>Temperature ({temperature})</label>
          <input type="number" min={0.01} max={2} step={0.05} value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))} />
        </div>
        <div>
          <label>Top-p ({topP})</label>
          <input type="number" min={0.01} max={1} step={0.05} value={topP}
            onChange={(e) => setTopP(Number(e.target.value))} />
        </div>
        <div>
          <label>Top-k ({topK})</label>
          <input type="number" min={0} max={200} value={topK}
            onChange={(e) => setTopK(Number(e.target.value))} />
        </div>
        <div>
          <label>Seed (optional)</label>
          <input type="number" min={0} value={seed}
            onChange={(e) => setSeed(e.target.value)}
            placeholder="leave empty for random" />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", paddingTop: "1.4rem" }}>
          <input type="checkbox" id="doSample" checked={doSample}
            onChange={(e) => setDoSample(e.target.checked)} />
          <label htmlFor="doSample" style={{ margin: 0 }}>Sampling (do_sample)</label>
        </div>
      </div>

      <button className="submit" onClick={submit} disabled={loading}>
        {loading ? "Generating…" : "Generate"}
      </button>
      {error && <div className="error-box">{error}</div>}
      {result && (
        <div className="result">
          <div style={{ marginBottom: "0.5rem", color: "#888", fontSize: "0.8rem" }}>
            {result.num_generated_tokens} tokens generated in {result.latency_ms}ms &nbsp;·&nbsp;
            model: {result.model}
          </div>
          <strong>Generated:</strong>
          <pre>{result.generated_text}</pre>
          <details style={{ marginTop: "0.6rem" }}>
            <summary style={{ cursor: "pointer", color: "#888", fontSize: "0.8rem" }}>Full text</summary>
            <pre style={{ marginTop: "0.4rem" }}>{result.full_text}</pre>
          </details>
        </div>
      )}
    </div>
  );
}
