"use client";

import { useState } from "react";

interface ColorPreset { name: string; hex: string; }
interface ColorPickerProps { presets: ColorPreset[]; selected: string; onChange: (hex: string) => void; }

export function ColorPicker({ presets, selected, onChange }: ColorPickerProps) {
  const [custom, setCustom] = useState("");
  return (
    <div className="space-y-3">
      <p className="text-sm font-medium">Brand Color</p>
      <div className="flex flex-wrap gap-2">
        {presets.map(p => (
          <button key={p.name} onClick={() => onChange(p.hex)} title={p.name}
            className={`h-8 w-8 rounded-full border-2 transition ${selected === p.hex ? "border-gray-900 dark:border-white scale-110" : "border-transparent"}`}
            style={{ backgroundColor: p.hex }} />
        ))}
      </div>
      <div className="flex items-center gap-2">
        <input type="text" placeholder="#FF5500" value={custom} onChange={e => setCustom(e.target.value)}
          className="rounded border px-2 py-1 text-sm dark:bg-gray-800 dark:border-gray-600 w-24" />
        <button onClick={() => { if (/^#[0-9A-Fa-f]{6}$/.test(custom)) onChange(custom); }}
          className="rounded bg-gray-200 px-2 py-1 text-xs dark:bg-gray-700">Apply</button>
      </div>
      {selected && (
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded" style={{ backgroundColor: selected }} />
          <span className="text-xs text-gray-500">{selected}</span>
        </div>
      )}
    </div>
  );
}
