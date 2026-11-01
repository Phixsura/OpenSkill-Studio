"use client";

import { useState } from "react";

interface Entry { title: string; version: string; category: string; date: string; }

const CAT_COLOR: Record<string, string> = {
  feature: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  bugfix: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  security: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  breaking: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
};

export default function ChangelogRssCard() {
  const [entries] = useState<Entry[]>([
    { title: "New Batch API", version: "2.1.0", category: "feature", date: "Oct 28" },
    { title: "Auth Fix", version: "2.0.1", category: "bugfix", date: "Oct 25" },
    { title: "V1 Removal", version: "2.0.0", category: "breaking", date: "Oct 20" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Changelog RSS</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">RSS/Atom feed for changelogs</p>

      <div className="mt-4 space-y-2">
        {entries.map((e) => (
          <div key={e.title} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${CAT_COLOR[e.category] ?? "bg-zinc-100 text-zinc-600"}`}>{e.category}</span>
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{e.title}</span>
            </div>
            <span className="text-xs text-zinc-400">v{e.version} · {e.date}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{entries.length} feed entries</div>
    </div>
  );
}
