"use client";

import { useState } from "react";

interface Flag {
  flagId: string;
  name: string;
  enabled: boolean;
  rolloutPct: number;
}

export default function FeatureFlagCard() {
  const [flags] = useState<Flag[]>([
    { flagId: "f1", name: "New Dashboard", enabled: true, rolloutPct: 100 },
    { flagId: "f2", name: "V2 Search", enabled: true, rolloutPct: 25 },
    { flagId: "f3", name: "Beta Analytics", enabled: false, rolloutPct: 0 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Feature Flags
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Per-endpoint feature toggles with rollout percentage
      </p>

      <div className="mt-4 space-y-2">
        {flags.map((f) => (
          <div
            key={f.flagId}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${f.enabled ? "bg-green-500" : "bg-zinc-300 dark:bg-zinc-600"}`} />
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{f.name}</span>
            </div>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              {f.enabled ? `${f.rolloutPct}% rollout` : "disabled"}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {flags.filter((f) => f.enabled).length}/{flags.length} flags active
      </div>
    </div>
  );
}
