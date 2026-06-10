import { useEffect, useState } from "react";
import { EncodePanel } from "./components/EncodePanel";
import { DecodePanel } from "./components/DecodePanel";
import { GeneratePanel } from "./components/GeneratePanel";
import { HistoryPanel } from "./components/HistoryPanel";

type Tab = "generate" | "encode" | "decode" | "history";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "generate", label: "Generate", icon: "✦" },
  { id: "encode",   label: "Encode",   icon: "→" },
  { id: "decode",   label: "Decode",   icon: "←" },
  { id: "history",  label: "History",  icon: "⊞" },
];

type ApiStatus = "checking" | "ready" | "error";

export default function App() {
  const [tab, setTab] = useState<Tab>("generate");
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [modelName, setModelName] = useState<string>("");

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/v1/readyz");
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

  return (
    <div>
      <header className="header">
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
          {modelName && (
            <span className="model-badge">{modelName}</span>
          )}
          <div className={`status-badge ${apiStatus}`}>
            <span className="status-dot" />
            {apiStatus === "ready" && "API ready"}
            {apiStatus === "checking" && "Connecting…"}
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
