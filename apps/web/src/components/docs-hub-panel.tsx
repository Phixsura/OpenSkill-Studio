"use client";
import { useState } from "react";

interface DocEntry { slug: string; title: string; category: string; read: boolean; }
interface ReadingProgress { read: number; total: number; percent: number; }

export function DocsHubPanel({ docs, progress, categories, onSelect, onSearch }: {
  docs: DocEntry[]; progress: ReadingProgress; categories: string[];
  onSelect?: (slug: string) => void; onSearch?: (q: string) => void;
}) {
  const [search, setSearch] = useState("");
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📚 Documentation</h2>
        <span className="text-sm text-gray-500">{progress.percent}% read</span>
      </div>
      <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); onSearch?.(e.target.value); }}
        placeholder="Search docs..." className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
      <div className="space-y-0.5">
        {docs.map((d) => (
          <button key={d.slug} onClick={() => onSelect?.(d.slug)}
            className="w-full text-left rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <span className={d.read ? "text-green-500" : "text-gray-300"}>{d.read ? "✅" : "○"}</span>
            <span className="text-sm">{d.title}</span>
            <span className="text-xs text-gray-400 ml-auto">{d.category}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
