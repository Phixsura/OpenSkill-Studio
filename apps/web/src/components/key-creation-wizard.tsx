"use client";
import { useState } from "react";

interface Scope { id: string; label: string; description: string; risk: string; }
interface KeyCreationWizardProps { scopes: Scope[];
  onCreate: (name: string, selectedScopes: string[]) => void; }

const RISK_COLOR: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

export function KeyCreationWizard({ scopes, onCreate }: KeyCreationWizardProps) {
  const [name, setName] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const toggle = (id: string) => setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-lg">
      <h3 className="font-semibold mb-3">🔑 Create API Key</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Key name (e.g. CI/CD)"
        className="w-full text-sm px-3 py-2 border rounded mb-3 dark:bg-gray-800 dark:border-gray-600" />
      <p className="text-xs font-medium text-gray-400 mb-2">Select Scopes</p>
      <div className="space-y-1.5 mb-4">
        {scopes.map(s => (
          <label key={s.id} className="flex items-center gap-2 text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-2 cursor-pointer">
            <input type="checkbox" checked={selected.includes(s.id)} onChange={() => toggle(s.id)} />
            <span className="flex-1">{s.label} <span className="text-xs text-gray-400">— {s.description}</span></span>
            <span className={`text-xs ${RISK_COLOR[s.risk] || ""}`}>{s.risk}</span>
          </label>
        ))}
      </div>
      <button onClick={() => name && selected.length && onCreate(name, selected)}
        disabled={!name || !selected.length}
        className="w-full py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50">
        Create Key ({selected.length} scopes)
      </button>
    </div>
  );
}
