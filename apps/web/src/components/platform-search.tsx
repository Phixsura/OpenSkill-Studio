"use client";

import { useState } from "react";

interface SearchResult { name: string; type: string; description: string; matchField: string; }
interface PlatformSearchProps { results: SearchResult[]; totalMatches: number;
  byType: Record<string, number>; onSearch: (q: string) => void; }

const TYPE_ICONS: Record<string, string> = {
  service: "⚙️", deployment: "🚀", incident: "🚨", runbook: "📋",
  config: "⚙️", user: "👤", team: "👥", doc: "📄",
};

export function PlatformSearch({ results, totalMatches, byType, onSearch }: PlatformSearchProps) {
  const [q, setQ] = useState("");
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <input value={q} onChange={e => { setQ(e.target.value); onSearch(e.target.value); }}
          placeholder="Search platform..." className="w-full px-3 py-2 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600" />
      </div>
      {totalMatches > 0 && (
        <>
          <div className="px-4 py-1.5 border-b dark:border-gray-700 text-[10px] text-gray-400">
            {totalMatches} results · {Object.entries(byType).map(([t, c]) => `${t}: ${c}`).join(", ")}
          </div>
          <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
            {results.map((r, i) => (
              <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs hover:bg-gray-50 dark:hover:bg-gray-800">
                <span>{TYPE_ICONS[r.type] ?? "📦"}</span>
                <div>
                  <div className="font-medium">{r.name}</div>
                  <div className="text-[10px] text-gray-400">{r.description}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
