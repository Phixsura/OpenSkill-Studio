"use client";

import { useState } from "react";

interface TagInfo { tag: string; count: number; color: string; }

export default function TagManagerCard() {
  const [tags] = useState<TagInfo[]>([
    { tag: "auth", count: 8, color: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300" },
    { tag: "users", count: 5, color: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" },
    { tag: "billing", count: 4, color: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300" },
    { tag: "v2", count: 12, color: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300" },
    { tag: "deprecated", count: 2, color: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Tag Manager</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Tag-based endpoint organization</p>

      <div className="mt-4 flex flex-wrap gap-2">
        {tags.map((t) => (
          <span key={t.tag} className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-medium ${t.color}`}>
            {t.tag}
            <span className="text-xs opacity-70">({t.count})</span>
          </span>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {tags.length} tags · {tags.reduce((s, t) => s + t.count, 0)} total assignments
      </div>
    </div>
  );
}
