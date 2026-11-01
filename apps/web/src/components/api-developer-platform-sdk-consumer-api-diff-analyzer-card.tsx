"use client";

import { useState } from "react";

interface DiffInfo {
  endpoint: string;
  fromVer: string;
  toVer: string;
  added: number;
  removed: number;
  breaking: boolean;
}

export default function DiffAnalyzerCard() {
  const [diffs] = useState<DiffInfo[]>([
    { endpoint: "/api/users", fromVer: "v1", toVer: "v2", added: 3, removed: 0, breaking: false },
    { endpoint: "/api/orders", fromVer: "v1", toVer: "v2", added: 1, removed: 2, breaking: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">API Diff Analyzer</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Compare API responses across versions</p>

      <div className="mt-4 space-y-2">
        {diffs.map((d) => (
          <div key={d.endpoint} className="rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{d.endpoint}</span>
              {d.breaking && <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs font-bold text-red-700 dark:bg-red-900 dark:text-red-300">BREAKING</span>}
            </div>
            <div className="mt-1 text-xs text-zinc-400">
              {d.fromVer} → {d.toVer} · +{d.added} added · -{d.removed} removed
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {diffs.filter((d) => d.breaking).length} breaking change{diffs.filter((d) => d.breaking).length !== 1 ? "s" : ""} detected
      </div>
    </div>
  );
}
