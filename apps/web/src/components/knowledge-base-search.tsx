"use client";

import { useState } from "react";

interface Article { id: string; title: string; category: string; content: string; tags: string[]; }
interface KnowledgeBaseSearchProps { articles: Article[]; onSelect: (id: string) => void; }

export function KnowledgeBaseSearch({ articles, onSelect }: KnowledgeBaseSearchProps) {
  const [query, setQuery] = useState("");
  const filtered = query.length >= 2
    ? articles.filter(a => a.title.toLowerCase().includes(query.toLowerCase()) || a.tags.some(t => t.includes(query.toLowerCase())))
    : articles.slice(0, 5);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Knowledge Base</h3>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search articles..."
        className="mt-2 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      <ul className="mt-3 space-y-2">
        {filtered.map(a => (
          <li key={a.id}>
            <button onClick={() => onSelect(a.id)} className="w-full rounded p-2 text-left hover:bg-gray-50 dark:hover:bg-gray-800">
              <p className="text-sm font-medium">{a.title}</p>
              <p className="text-xs text-gray-500 line-clamp-1">{a.content}</p>
              <div className="mt-1 flex gap-1">{a.tags.slice(0, 3).map(t => (
                <span key={t} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">{t}</span>
              ))}</div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
