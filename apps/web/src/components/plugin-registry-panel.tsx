"use client";

import { useState } from "react";

interface Plugin {
  pluginId: string;
  name: string;
  version: string;
  description: string;
  tags: string[];
  enabled: boolean;
  dependencies: string[];
}

export function PluginRegistryPanel({
  plugins,
  onToggle,
  onUninstall,
  onSearch,
}: {
  plugins: Plugin[];
  onToggle?: (name: string) => void;
  onUninstall?: (name: string) => void;
  onSearch?: (query: string) => void;
}) {
  const [search, setSearch] = useState("");
  const enabled = plugins.filter((p) => p.enabled).length;

  const handleSearch = (q: string) => { setSearch(q); onSearch?.(q); };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🧩 Plugins</h2>
        <span className="text-sm text-gray-500">{enabled}/{plugins.length} enabled</span>
      </div>

      <input type="text" value={search} onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search plugins..." className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />

      <div className="space-y-1">
        {plugins.map((p) => (
          <div key={p.pluginId} className={`rounded-lg border dark:border-gray-700 p-3 ${!p.enabled ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{p.name}</span>
                <span className="text-xs text-gray-400">v{p.version}</span>
              </div>
              <div className="flex gap-1">
                <button onClick={() => onToggle?.(p.name)}
                  className={`text-xs px-2 py-0.5 rounded ${p.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {p.enabled ? "On" : "Off"}
                </button>
                <button onClick={() => onUninstall?.(p.name)} className="text-xs text-red-500">✕</button>
              </div>
            </div>
            {p.description && <p className="text-xs text-gray-500">{p.description}</p>}
            <div className="flex gap-1 mt-1">
              {p.tags.map((t) => (
                <span key={t} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{t}</span>
              ))}
              {p.dependencies.length > 0 && (
                <span className="text-xs text-purple-500">deps: {p.dependencies.join(", ")}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
