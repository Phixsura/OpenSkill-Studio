"use client";

import { useState } from "react";

interface Preset { id: string; logs: number; analytics: number; userData: number; }

const PRESETS: Preset[] = [
  { id: "minimal", logs: 7, analytics: 30, userData: 90 },
  { id: "standard", logs: 30, analytics: 180, userData: 365 },
  { id: "gdpr_compliant", logs: 30, analytics: 90, userData: 365 },
  { id: "extended", logs: 90, analytics: 365, userData: 730 },
];

interface DataRetentionConfigProps { activePreset: string; onSave: (preset: string) => void; }

export function DataRetentionConfig({ activePreset, onSave }: DataRetentionConfigProps) {
  const [selected, setSelected] = useState(activePreset);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Data Retention Policy</h3>
      <div className="mt-3 grid grid-cols-2 gap-2">
        {PRESETS.map(p => (
          <button key={p.id} onClick={() => setSelected(p.id)}
            className={`rounded-lg border p-3 text-left text-sm ${selected === p.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700"}`}>
            <p className="font-semibold capitalize">{p.id.replace("_", " ")}</p>
            <p className="text-xs text-gray-400">Logs: {p.logs}d · Analytics: {p.analytics}d</p>
          </button>
        ))}
      </div>
      <button onClick={() => onSave(selected)} className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white">
        Apply Policy
      </button>
    </div>
  );
}
