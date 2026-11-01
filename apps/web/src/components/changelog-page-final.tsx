"use client";

import { useState } from "react";

interface Entry { title: string; date: string; entry_type: string; description?: string; }
interface ChangelogPageFinalProps { entries: Entry[]; filterOptions: string[]; activeFilter: string;
  onFilterChange: (filter: string) => void; rssUrl: string; }

const TYPE_ICONS: Record<string, string> = { platform: "🏗️", app: "📦", api: "🔌" };

export function ChangelogPageFinal({ entries, filterOptions, activeFilter, onFilterChange, rssUrl }: ChangelogPageFinalProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Changelog</h1>
        <a href={rssUrl} className="rounded border px-3 py-1 text-sm text-orange-600">RSS</a>
      </div>
      <div className="flex gap-1">
        {filterOptions.map(f => (
          <button key={f} onClick={() => onFilterChange(f)}
            className={`rounded-full px-3 py-1 text-xs capitalize ${activeFilter === f ? "bg-blue-600 text-white" : "border border-gray-200 text-gray-500 dark:border-gray-700"}`}>
            {f}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {entries.map((e, i) => (
          <div key={i} className="border-l-2 border-blue-300 pl-4">
            <div className="flex items-center gap-2">
              <span>{TYPE_ICONS[e.entry_type] || "📌"}</span>
              <span className="text-xs text-gray-400">{e.date}</span>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs capitalize dark:bg-gray-700">{e.entry_type}</span>
            </div>
            <h3 className="mt-1 font-semibold">{e.title}</h3>
            {e.description && <p className="text-sm text-gray-500">{e.description}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
