"use client";

import { useState } from "react";

interface Entry { type: string; text: string; icon: string; }
interface Release { version: string; date: string; entries: Entry[]; hasBreaking: boolean; }
interface ChangelogPageViewProps { appName: string; releases: Release[]; totalEntries: number;
  availableFilters: string[]; onFilter: (type: string | null) => void; }

export function ChangelogPageView({ appName, releases, totalEntries, availableFilters, onFilter }: ChangelogPageViewProps) {
  const [filter, setFilter] = useState<string | null>(null);
  const apply = (f: string | null) => { setFilter(f); onFilter(f); };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📝 {appName} Changelog</h2>
        <span className="text-xs text-gray-400">{totalEntries} changes</span>
      </div>
      <div className="flex gap-1">
        <button onClick={() => apply(null)}
          className={`rounded px-2 py-0.5 text-xs ${!filter ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {availableFilters.map(f => (
          <button key={f} onClick={() => apply(f)}
            className={`rounded px-2 py-0.5 text-xs capitalize ${filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{f}</button>
        ))}
      </div>
      {releases.map(r => (
        <div key={r.version} className="rounded-xl border p-4 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-bold">v{r.version}</span>
            {r.hasBreaking && <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
            <span className="ml-auto text-xs text-gray-400">{r.date}</span>
          </div>
          <ul className="space-y-1">
            {r.entries.map((e, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-xs">{e.icon}</span><span>{e.text}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
