import { useCallback, useState } from "react";
import { api, isApiError, type GenerateResponse } from "../api";

export function GeneratePanel() {
  const [prompt, setPrompt] = useState("Once upon a time");
  const [maxTokens, setMaxTokens] = useState(80);
  const [temperature, setTemperature] = useState(0.8);
  const [topP, setTopP] = useState(0.95);
  const [topK, setTopK] = useState(50);
  const [doSample, setDoSample] = useState(true);
  const [seed, setSeed] = useState<string>("");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const submit = useCallback(async () => {
    if (!prompt.trim()) return;
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
  }, [prompt, maxTokens, temperature, topP, topK, doSample, seed]);

  function onKeyDown(e: React.KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") void submit();
  }

  function copyOutput() {
    if (!result) return;
    void navigator.clipboard.writeText(result.generated_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <div className="panel-title">Text Generation</div>
          <div className="panel-desc">Generate text from a prompt using GPT-2 inference</div>
        </div>
      </div>

      <div className="field">
        <label>Prompt <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(⌘ Enter to generate)</span></label>
        <textarea
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Start your story…"
        />
      </div>

      <div className="divider" />

      <div className="grid2" style={{ marginBottom: "1rem" }}>
        <div className="field">
          <label>Max new tokens</label>
          <div className="slider-row">
            <input
              type="range" min={1} max={512} step={1}
              value={maxTokens}
              onChange={(e) => setMaxTokens(Number(e.target.value))}
            />
            <span className="slider-value">{maxTokens}</span>
          </div>
        </div>

        <div className="field">
          <label>Temperature {!doSample && <span style={{ color: "var(--text-muted)" }}>(greedy)</span>}</label>
          <div className="slider-row">
            <input
              type="range" min={0.01} max={2} step={0.01}
              value={temperature}
              disabled={!doSample}
              onChange={(e) => setTemperature(Number(e.target.value))}
              style={{ opacity: doSample ? 1 : 0.35 }}
            />
            <span className="slider-value" style={{ opacity: doSample ? 1 : 0.35 }}>
              {temperature.toFixed(2)}
            </span>
          </div>
        </div>

        <div className="field">
          <label>Top-p (nucleus)</label>
          <div className="slider-row">
            <input
              type="range" min={0.01} max={1} step={0.01}
              value={topP}
              disabled={!doSample}
              onChange={(e) => setTopP(Number(e.target.value))}
              style={{ opacity: doSample ? 1 : 0.35 }}
            />
            <span className="slider-value" style={{ opacity: doSample ? 1 : 0.35 }}>
              {topP.toFixed(2)}
            </span>
          </div>
        </div>

        <div className="field">
          <label>Top-k</label>
          <div className="slider-row">
            <input
              type="range" min={0} max={200} step={1}
              value={topK}
              disabled={!doSample}
              onChange={(e) => setTopK(Number(e.target.value))}
              style={{ opacity: doSample ? 1 : 0.35 }}
            />
            <span className="slider-value" style={{ opacity: doSample ? 1 : 0.35 }}>{topK}</span>
          </div>
        </div>
      </div>

      <div className="grid2">
        <div className="toggle-row">
          <div>
            <div className="toggle-label">Sampling</div>
            <div className="toggle-desc">Random sampling vs greedy decoding</div>
          </div>
          <label className="toggle">
            <input type="checkbox" checked={doSample} onChange={(e) => setDoSample(e.target.checked)} />
            <span className="toggle-track" />
          </label>
        </div>

        <div className="field">
          <label>Seed <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(optional, for reproducibility)</span></label>
          <input
            type="number" min={0}
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
            placeholder="random"
          />
        </div>
      </div>

      <div className="row" style={{ marginTop: "1.25rem" }}>
        <button className="btn btn-primary" onClick={submit} disabled={loading || !prompt.trim()}>
          {loading ? <><span className="spinner" /> Generating…</> : "✦ Generate"}
        </button>
        {result && (
          <>
            <span className="badge badge-green">{result.num_generated_tokens} tokens</span>
            <span className="badge badge-muted">{result.latency_ms}ms</span>
          </>
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
              <span className="badge badge-green">{result.num_generated_tokens} new tokens</span>
              <span className="badge badge-muted">{result.latency_ms}ms</span>
              <span className="model-badge">{result.model}</span>
            </div>
            <div className="row" style={{ gap: "0.5rem" }}>
              {copied && <span className="copy-hint">Copied!</span>}
              <button className="btn-icon" onClick={copyOutput} title="Copy generated text">⎘</button>
            </div>
          </div>

          <div className="result-body">
            <div className="section-label">Generated text</div>
            <div className="result-text" style={{ marginTop: "0.4rem" }}>
              <span className="gen-output">{result.generated_text}</span>
            </div>

            <details style={{ marginTop: "0.75rem" }}>
              <summary>Full text (prompt + generation)</summary>
              <div className="result-text">
                <span className="gen-prompt">{result.prompt}</span>
                <span className="gen-output">{result.generated_text}</span>
              </div>
            </details>

            <details>
              <summary>Parameters used</summary>
              <pre className="summary-pre">{JSON.stringify(result.params, null, 2)}</pre>
            </details>
          </div>
        </div>
      )}
    </div>
  );
}
