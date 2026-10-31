"use client";

import { useState } from "react";

interface PackageInfo {
  name: string;
  version: string;
  sizeKb: number;
}

interface EnvSummary {
  runtime: string;
  packages: number;
  apis: number;
  envVars: number;
  issues: number;
}

export function EnvInspectorPanel({
  summary,
  packages,
  availableApis,
  diagnostics,
  onRefresh,
}: {
  summary: EnvSummary;
  packages: PackageInfo[];
  availableApis: string[];
  diagnostics: string[];
  onRefresh?: () => void;
}) {
  const [tab, setTab] = useState<"overview" | "packages" | "apis" | "diagnostics">("overview");
  const [pkgSearch, setPkgSearch] = useState("");
  const filteredPkgs = pkgSearch
    ? packages.filter((p) => p.name.toLowerCase().includes(pkgSearch.toLowerCase()))
    : packages;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔎 Env Inspector</h2>
        <div className="flex items-center gap-2">
          <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{summary.runtime}</code>
          <button onClick={onRefresh} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Refresh</button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Packages</span>
          <span className="font-bold text-lg">{summary.packages}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">APIs</span>
          <span className="font-bold text-lg">{summary.apis}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Env Vars</span>
          <span className="font-bold text-lg">{summary.envVars}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Issues</span>
          <span className={`font-bold text-lg ${summary.issues > 0 ? "text-red-600" : "text-green-600"}`}>{summary.issues}</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["overview", "packages", "apis", "diagnostics"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "diagnostics" ? `Issues (${diagnostics.length})` : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "packages" && (
        <div className="space-y-2">
          <input type="text" value={pkgSearch} onChange={(e) => setPkgSearch(e.target.value)}
            placeholder="Search packages..." className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
          {filteredPkgs.map((p) => (
            <div key={p.name} className="flex justify-between text-sm rounded-lg border dark:border-gray-700 p-2">
              <code>{p.name}</code>
              <span className="text-xs text-gray-400">{p.version} · {p.sizeKb}KB</span>
            </div>
          ))}
        </div>
      )}

      {tab === "apis" && (
        <div className="flex flex-wrap gap-1">
          {availableApis.map((api) => (
            <span key={api} className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 px-2 py-0.5 rounded-full">{api}</span>
          ))}
        </div>
      )}

      {tab === "diagnostics" && (
        <div className="space-y-1">
          {diagnostics.length === 0 && <span className="text-sm text-green-600">No issues found</span>}
          {diagnostics.map((d, i) => (
            <div key={i} className="text-xs text-red-500 rounded-lg border border-red-300 dark:border-red-700 p-2">⚠ {d}</div>
          ))}
        </div>
      )}
    </div>
  );
}
