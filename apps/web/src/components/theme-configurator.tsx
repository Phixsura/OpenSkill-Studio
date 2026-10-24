"use client";

import { useState } from "react";

interface ThemeConfiguratorProps { colors: Record<string, string>; font: string;
  borderRadius: number; availableFonts: string[]; onChange: (config: Record<string, unknown>) => void; }

export function ThemeConfigurator({ colors, font, borderRadius, availableFonts, onChange }: ThemeConfiguratorProps) {
  const [cfg, setCfg] = useState({ ...colors, font, borderRadius });

  const update = (key: string, value: string | number) => {
    const next = { ...cfg, [key]: value };
    setCfg(next);
    onChange(next);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Theme</h3>
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(colors).map(([name, val]) => (
          <div key={name}>
            <label className="block text-xs text-gray-400 capitalize mb-1">{name}</label>
            <div className="flex items-center gap-2">
              <input type="color" value={cfg[name] ?? val}
                onChange={e => update(name, e.target.value)} className="h-8 w-8 rounded cursor-pointer" />
              <input type="text" value={cfg[name] ?? val}
                onChange={e => update(name, e.target.value)}
                className="flex-1 rounded border px-2 py-1 text-xs font-mono dark:bg-gray-800 dark:border-gray-600" />
            </div>
          </div>
        ))}
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Font</label>
        <select value={cfg.font} onChange={e => update("font", e.target.value)}
          className="w-full rounded border px-2 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600">
          {availableFonts.map(f => <option key={f}>{f}</option>)}
        </select>
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Border Radius: {cfg.borderRadius}px</label>
        <input type="range" min={0} max={24} value={cfg.borderRadius}
          onChange={e => update("borderRadius", Number(e.target.value))} className="w-full" />
      </div>
    </div>
  );
}
