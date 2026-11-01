"use client";

import { useState } from "react";

export default function ResponseCacheCard() {
  const [stats] = useState({
    entries: 847,
    maxEntries: 1000,
    sizeMB: 12.4,
    hitRate: 87.3,
    totalHits: 45200,
    totalMisses: 6580,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Response Cache
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        LRU response cache with TTL and invalidation
      </p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-xl font-bold text-green-600 dark:text-green-400">{stats.hitRate}%</div>
          <div className="text-xs text-zinc-500">Hit Rate</div>
        </div>
        <div>
          <div className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{stats.entries}</div>
          <div className="text-xs text-zinc-500">Entries</div>
        </div>
        <div>
          <div className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{stats.sizeMB}MB</div>
          <div className="text-xs text-zinc-500">Size</div>
        </div>
      </div>

      <div className="mt-3 flex justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{stats.totalHits.toLocaleString()} hits</span>
        <span>{stats.totalMisses.toLocaleString()} misses</span>
      </div>
    </div>
  );
}
