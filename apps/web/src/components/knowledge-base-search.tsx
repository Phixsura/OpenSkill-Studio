"use client";

import { useState } from "react";

interface Article { id: string; title: string; category?: string; tags?: string[]; }
interface KnowledgeBaseSearchProps { articles: Article[]; onSearch: (query: string) => void;
  onSelect: (id: string) => void; }

export function KnowledgeBaseSearch({ articles, onSearch, onSelect }: KnowledgeBaseSearchProps) {
  const [query, setQuery] = useState("");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Help Center</h2>
      <div className="relative">
        <input value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }}
          placeholder="Search articles..." className="w-full rounded-lg border px-4 py-2.5 pl-10 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
      </div>
      <div className="space-y-2">
        {articles.map(a => (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className="flex w-full items-start gap-3 rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <span className="text-lg">📄</span>
            <div>
              <p className="text-sm font-medium">{a.title}</p>
              <div className="mt-1 flex gap-1">
                {a.category && <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{a.category}</span>}
                {a.tags?.map(t => (
                  <span key={t} className="rounded bg-blue-50 px-1.5 py-0.5 text-xs text-blue-600 dark:bg-blue-900/20">{t}</span>
                ))}
              </div>
            </div>
          </button>
        ))}
        {articles.length === 0 && <p className="text-center text-sm text-gray-400">No articles found</p>}
      </div>
    </div>
  );
}
