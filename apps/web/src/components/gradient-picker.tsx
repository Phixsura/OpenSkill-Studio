"use client";

import { useState } from "react";

interface GradientPreset { id: string; css: string; from: string; to: string; }
interface GradientPickerProps { presets: GradientPreset[]; onSelect: (css: string) => void; }

export function GradientPicker({ presets, onSelect }: GradientPickerProps) {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Gradient</h3>
      <div className="grid grid-cols-3 gap-2">
        {presets.map(p => (
          <button key={p.id} onClick={() => { setSelected(p.id); onSelect(p.css); }}
            className={`h-16 rounded-lg transition ${selected === p.id ? "ring-2 ring-blue-500 ring-offset-2" : ""}`}
            style={{ background: p.css }}>
            <span className="text-xs font-medium text-white drop-shadow capitalize">{p.id}</span>
          </button>
        ))}
      </div>
      {selected && (
        <code className="block rounded bg-gray-100 px-3 py-2 text-xs font-mono dark:bg-gray-800">
          {presets.find(p => p.id === selected)?.css}
        </code>
      )}
    </div>
  );
}
