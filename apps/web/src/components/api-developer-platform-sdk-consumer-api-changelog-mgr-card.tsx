"use client";

import { useState } from "react";

interface ChangeEntry { type: string; description: string; breaking: boolean; }
interface VersionLog { version: string; entries: ChangeEntry[]; }

const TYPE_COLOR: Record<string, string> = {
  added: "text-green-600 dark:text-green-400",
  changed: "text-blue-600 dark:text-blue-400",
  fixed: "text-amber-600 dark:text-amber-400",
  removed: "text-red-600 dark:text-red-400",
  deprecated: "text-orange-600 dark:text-orange-400",
  security: "text-purple-600 dark:text-purple-400",
};

export default function ChangelogManagerCard() {
  const [logs] = useState<VersionLog[]>([
    { version: "2.1.0", entries: [
      { type: "added", description: "Batch API support", breaking: false },
      { type: "fixed", description: "Rate limit edge case", breaking: false },
    ]},
    { version: "2.0.0", entries: [
      { type: "removed", description: "Legacy v1 endpoints", breaking: true },
      { type: "added", description: "OAuth 2.0 support", breaking: false },
    ]},
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Changelog</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Structured changelog with categories</p>

      <div className="mt-4 space-y-3">
        {logs.map((log) => (
          <div key={log.version} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="font-mono text-sm font-bold text-zinc-900 dark:text-zinc-100">v{log.version}</div>
            <ul className="mt-1 space-y-0.5">
              {log.entries.map((e, i) => (
                <li key={i} className="flex items-center gap-1 text-xs">
                  <span className={TYPE_COLOR[e.type] ?? "text-zinc-500"}>{e.type}</span>
                  <span className="text-zinc-600 dark:text-zinc-400">{e.description}</span>
                  {e.breaking && <span className="text-red-500 font-bold">BREAKING</span>}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {logs.length} versions documented
      </div>
    </div>
  );
}
