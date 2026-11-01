"use client";

import { useState } from "react";

interface CacheStats {
  totalEntries: number;
  totalTags: number;
  cascadeRules: number;
  totalInvalidations: number;
}

export default function CacheInvalidatorCard() {
  const [stats] = useState<CacheStats>({
    totalEntries: 1240,
    totalTags: 35,
    cascadeRules: 8,
    totalInvalidations: 456,
  });

  const [recentTags] = useState(["users", "orders", "products", "sessions"]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Cache Invalidator
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Tag-based cache invalidation with cascade
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3 text-center">
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.totalEntries.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Entries</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.totalTags}</div>
          <div className="text-xs text-zinc-500">Tags</div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {recentTags.map((t) => (
          <span key={t} className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900 dark:text-blue-300">
            {t}
          </span>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.cascadeRules} cascade rules · {stats.totalInvalidations} invalidations
      </div>
    </div>
  );
}
