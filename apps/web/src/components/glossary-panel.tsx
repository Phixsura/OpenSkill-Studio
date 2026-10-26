"use client";

import { useState } from "react";

interface Term { term: string; definition: string; category: string; related: string[]; example?: string; }

export function GlossaryPanel({ terms, categories, onSearch }: {
  terms: Term[]; categories: string[]; onSearch?: (q: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState<string>("all");

  const filtered = cat === "all" ? terms : terms.filter(t => t.category === cat);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📖 Glossary</h2>
      <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); onSearch?.(e.target.value); }}
        placeholder="Search terms..."
        className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
      <div className="flex gap-1 flex-wrap">
        <button onClick={() => setCat("all")}
          className={`text-xs px-2 py-0.5 rounded-full ${cat === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {categories.map(c => (
          <button key={c} onClick={() => setCat(c)}
            className={`text-xs px-2 py-0.5 rounded-full ${cat === c ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{c}</button>
        ))}
      </div>
      <div className="space-y-2">
        {filtered.map(t => (
          <div key={t.term} className="rounded-lg border dark:border-gray-700 p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-bold text-sm">{t.term}</span>
              <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{t.category}</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">{t.definition}</p>
            {t.related.length > 0 && (
              <div className="text-xs text-gray-400 mt-1">See also: {t.related.join(", ")}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
