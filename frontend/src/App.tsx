import { useState } from "react";
import { EncodePanel } from "./components/EncodePanel";
import { DecodePanel } from "./components/DecodePanel";
import { GeneratePanel } from "./components/GeneratePanel";
import { HistoryPanel } from "./components/HistoryPanel";

type Tab = "encode" | "decode" | "generate" | "history";

const TABS: { id: Tab; label: string }[] = [
  { id: "encode", label: "Encode" },
  { id: "decode", label: "Decode" },
  { id: "generate", label: "Generate" },
  { id: "history", label: "History" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("generate");

  return (
    <>
      <h1>🍽 Transformer Bistro</h1>
      <p className="subtitle">REST API playground for small open-source LLMs</p>
      <nav>
        {TABS.map((t) => (
          <button
            key={t.id}
            className={tab === t.id ? "active" : ""}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      {tab === "encode" && <EncodePanel />}
      {tab === "decode" && <DecodePanel />}
      {tab === "generate" && <GeneratePanel />}
      {tab === "history" && <HistoryPanel />}
    </>
  );
}
