"use client";

import { useState } from "react";

interface Metric { name: string; type: string; unit: string; labels: string[]; }
interface MetricExplorerProps { metrics: Metric[]; totalMetrics: number;
  byType: Record<string, number>; onSearch: (query: string) => void; }

const TYPE_COLORS: Record<string, string> = {
  counter: "bg-blue-100 text-blue-700", gauge: "bg-green-100 text-green-700",
  histogram: "bg-purple-100 text-purple-700", summary: "bg-yellow-100 text-yellow-700",
};

export function MetricExplorer({ metrics, totalMetrics, byType, onSearch }: MetricExplorerProps) {
  const [query, setQuery] = useState("");
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold mb-2">🔎 Metric Explorer</h3>
        <input value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }}
          placeholder="Search metrics..." className="w-full px-3 py-1.5 text-sm border rounded dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div className="flex gap-2 px-4 py-1.5 border-b dark:border-gray-700 text-[10px]">
        {Object.entries(byType).map(([t, c]) => (
          <span key={t} className={`px-1.5 py-0.5 rounded ${TYPE_COLORS[t] ?? ""}`}>{t}: {c}</span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
        {metrics.map(m => (
          <div key={m.name} className="px-4 py-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-medium">{m.name}</span>
              <span className={`px-1 py-0.5 text-[10px] rounded ${TYPE_COLORS[m.type] ?? ""}`}>{m.type}</span>
            </div>
            <div className="text-[10px] text-gray-400">{m.unit} · labels: {m.labels.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
