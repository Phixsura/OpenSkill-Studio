"use client";

import { useState } from "react";

interface SearchResult { name: string; type: string; description: string; score: number; }
interface GlobalSearchBarProps { results: SearchResult[]; totalMatches: number;
  byType: Record<string, number>; onSearch: (query: string) => void; }

const TYPE_ICONS: Record<string, string> = {
  app: "📦", user: "👤", team: "👥", webhook: "🔗", deployment: "🚀", document: "📄",
};

export function GlobalSearchBar({ results, totalMatches, byType, onSearch }: GlobalSearchBarProps) {
  const [query, setQuery] = useState("");
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-3 border-b dark:border-gray-700">
        <input value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }}
          placeholder="Search everything..." className="w-full px-3 py-2 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600" />
      </div>
      {totalMatches > 0 && (
        <>
          <div className="flex gap-2 px-3 py-1.5 border-b dark:border-gray-700 text-[10px]">
            {Object.entries(byType).map(([t, c]) => (
              <span key={t} className="text-gray-400">{TYPE_ICONS[t] ?? ""} {t}: {c}</span>
            ))}
          </div>
          <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
            {results.map((r, i) => (
              <div key={i} className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
                <span>{TYPE_ICONS[r.type] ?? "📦"}</span>
                <div>
                  <div className="text-sm font-medium">{r.name}</div>
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
