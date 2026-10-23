"use client";

import { useState } from "react";

interface SearchResult { type: string; title: string; subtitle: string; icon: string; href: string; }
interface GlobalSearchDialogProps { sections: Record<string, SearchResult[]>; total: number;
  onSearch: (query: string) => void; onSelect: (href: string) => void; onClose: () => void; }

export function GlobalSearchDialog({ sections, total, onSearch, onSelect, onClose }: GlobalSearchDialogProps) {
  const [query, setQuery] = useState("");
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[15vh]" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl border bg-white shadow-2xl dark:bg-gray-900 dark:border-gray-700" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-2 border-b px-4 py-3 dark:border-gray-700">
          <span>🔍</span>
          <input autoFocus value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }}
            placeholder="Search apps, docs, users..." className="flex-1 bg-transparent text-sm outline-none" />
          <kbd className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">ESC</kbd>
        </div>
        <div className="max-h-80 overflow-y-auto p-2">
          {Object.entries(sections).map(([section, items]) => (
            <div key={section} className="mb-2">
              <p className="px-2 py-1 text-xs font-semibold text-gray-400 uppercase">{section}</p>
              {items.map((r, i) => (
                <button key={i} onClick={() => onSelect(r.href)}
                  className="flex w-full items-center gap-2 rounded px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
                  <span>{r.icon}</span>
                  <div className="text-left"><p className="font-medium">{r.title}</p>
                    <p className="text-xs text-gray-400">{r.subtitle}</p></div>
                </button>
              ))}
            </div>
          ))}
          {total === 0 && query && <p className="py-6 text-center text-sm text-gray-400">No results</p>}
        </div>
      </div>
    </div>
  );
}
