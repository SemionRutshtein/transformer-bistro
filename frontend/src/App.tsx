import { useEffect, useState, Component, type ReactNode } from "react";
import { EncodePanel } from "./components/EncodePanel";
import { DecodePanel } from "./components/DecodePanel";
import { GeneratePanel } from "./components/GeneratePanel";
import { HistoryPanel } from "./components/HistoryPanel";
import { SparklesCore } from "./components/ui/SparklesCore";

class SparklesErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? null : this.props.children; }
}

type Tab = "generate" | "encode" | "decode" | "history";
type ApiStatus = "checking" | "ready" | "error";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "generate", label: "Generate", icon: "✦" },
  { id: "encode",   label: "Encode",   icon: "→" },
  { id: "decode",   label: "Decode",   icon: "←" },
  { id: "history",  label: "History",  icon: "⊞" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("generate");
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [modelName, setModelName] = useState<string>("");

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/readyz");
        if (res.ok) {
          const data = (await res.json()) as { model?: string };
          setModelName(data.model ?? "");
          setApiStatus("ready");
        } else {
          setApiStatus("error");
        }
      } catch {
        setApiStatus("error");
      }
    })();
  }, []);

  // ── Loading screen ────────────────────────────────────────────────────────
  if (apiStatus === "checking") {
    return (
      <div className="loading-screen">
        <div className="loading-sparkles">
          <SparklesErrorBoundary>
            <SparklesCore
              id="loading-sparkles"
              background="transparent"
              minSize={0.6}
              maxSize={1.4}
              particleDensity={100}
              className="w-full h-full"
              particleColor="#818cf8"
              speed={1}
            />
          </SparklesErrorBoundary>
        </div>
        <div className="loading-content">
          <div className="loading-logo">🍽</div>
          <h1 className="loading-title">Transformer Bistro</h1>
          <div className="loading-sparkles-line">
            <div className="loading-gradient-left" />
            <div className="loading-gradient-right" />
            <SparklesErrorBoundary>
              <SparklesCore
                id="loading-line-sparkles"
                background="transparent"
                minSize={0.4}
                maxSize={1}
                particleDensity={1200}
                className="w-full h-full"
                particleColor="#818cf8"
                speed={2}
              />
            </SparklesErrorBoundary>
            <div className="loading-mask" />
          </div>
          <div className="loading-status">
            <span className="loading-dot" />
            Loading model…
          </div>
        </div>
      </div>
    );
  }

  // ── Main app ──────────────────────────────────────────────────────────────
  return (
    <div>
      {/* Header with subtle sparkles */}
      <header className="header">
        <div className="header-sparkles-bg">
          <SparklesErrorBoundary>
            <SparklesCore
              id="header-sparkles"
              background="transparent"
              minSize={0.3}
              maxSize={0.9}
              particleDensity={30}
              className="w-full h-full"
              particleColor="#818cf8"
              speed={0.8}
            />
          </SparklesErrorBoundary>
        </div>

        <div className="header-left">
          <div className="header-title">
            <div className="logo-icon">🍽</div>
            Transformer Bistro
          </div>
          <div className="header-subtitle">
            REST API playground for open-source LLMs
          </div>
        </div>

        <div className="row" style={{ gap: "0.75rem" }}>
          {modelName && <span className="model-badge">{modelName}</span>}
          <div className={`status-badge ${apiStatus}`}>
            <span className="status-dot" />
            {apiStatus === "ready" && "API ready"}
            {apiStatus === "error" && "Unavailable"}
          </div>
        </div>
      </header>

      <nav className="tabs" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={`tab-btn${tab === t.id ? " active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            <span className="tab-icon">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "generate" && <GeneratePanel />}
      {tab === "encode"   && <EncodePanel />}
      {tab === "decode"   && <DecodePanel />}
      {tab === "history"  && <HistoryPanel />}
    </div>
  );
}
