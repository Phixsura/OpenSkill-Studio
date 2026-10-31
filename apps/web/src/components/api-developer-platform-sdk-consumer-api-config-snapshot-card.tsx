"use client";

import { useState } from "react";

interface Snapshot { id: string; label: string; keys: number; date: string; }

export default function ConfigSnapshotCard() {
  const [snapshots] = useState<Snapshot[]>([
    { id: "snap-3", label: "Production v2.1", keys: 15, date: "2024-10-28" },
    { id: "snap-2", label: "Before migration", keys: 12, date: "2024-10-15" },
    { id: "snap-1", label: "Initial setup", keys: 8, date: "2024-09-01" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Config Snapshots</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Configuration snapshots with rollback</p>

      <div className="mt-4 space-y-2">
        {snapshots.map((s) => (
          <div key={s.id} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{s.label}</span>
              <span className="ml-2 text-xs text-zinc-400">{s.keys} keys</span>
            </div>
            <span className="text-xs text-zinc-400">{s.date}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{snapshots.length} snapshots saved</div>
    </div>
  );
}
