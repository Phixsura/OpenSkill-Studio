"use client";

import { useState } from "react";

interface ClipEntry { preview: string; source: string; charCount: number; timestamp: string; }
interface ClipboardHistoryProps { items: ClipEntry[]; total: number; onClear: () => void; }

export function ClipboardHistoryPanel({ items, total, onClear }: ClipboardHistoryProps) {
  const [query, setQuery] = useState("");
  const filtered = query ? items.filter(i => i.preview.toLowerCase().includes(query.toLowerCase())) : items;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Clipboard History</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{total} items</span>
          <button onClick={onClear} className="text-xs text-red-600 hover:underline">Clear</button>
        </div>
      </div>
      <input type="text" placeholder="Search..." value={query} onChange={e => setQuery(e.target.value)}
        className="w-full rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <div className="max-h-64 space-y-1 overflow-y-auto">
        {filtered.map((item, i) => (
          <div key={i} className="rounded border px-3 py-2 text-sm dark:border-gray-700">
            <p className="font-mono text-xs truncate">{item.preview}</p>
            <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
              <span>{item.source}</span>
              <span>{item.charCount} chars</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
