"use client";

interface ApiVersionSwitcherProps { versions: string[]; active: string; onSwitch: (v: string) => void; deprecated?: string[]; }

export function ApiVersionSwitcher({ versions, active, onSwitch, deprecated = [] }: ApiVersionSwitcherProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-gray-500">API Version:</span>
      {versions.map(v => (
        <button key={v} onClick={() => onSwitch(v)}
          className={`rounded px-3 py-1 text-sm transition ${active === v ? "bg-blue-600 text-white" : "border border-gray-200 text-gray-600 hover:bg-gray-50 dark:border-gray-700"} ${deprecated.includes(v) ? "line-through opacity-60" : ""}`}>
          {v} {deprecated.includes(v) && <span className="text-xs">(deprecated)</span>}
        </button>
      ))}
    </div>
  );
}
