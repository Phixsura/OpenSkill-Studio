"use client";

import { useState } from "react";

interface LaneInfo { priority: string; consumers: number; color: string; }

export default function TrafficShaperCard() {
  const [lanes] = useState<LaneInfo[]>([
    { priority: "critical", consumers: 2, color: "bg-red-500" },
    { priority: "high", consumers: 5, color: "bg-orange-500" },
    { priority: "normal", consumers: 15, color: "bg-blue-500" },
    { priority: "low", consumers: 8, color: "bg-zinc-400" },
    { priority: "background", consumers: 3, color: "bg-zinc-300" },
  ]);

  const [globalRps] = useState({ current: 4500, max: 10000 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Traffic Shaper</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Traffic shaping with priority lanes</p>

      <div className="mt-4 flex gap-1 h-3 rounded-full overflow-hidden bg-zinc-100 dark:bg-zinc-800">
        {lanes.map((l) => (
          <div key={l.priority} className={`${l.color}`} style={{ flex: l.consumers }} />
        ))}
      </div>

      <div className="mt-2 flex flex-wrap gap-2">
        {lanes.map((l) => (
          <div key={l.priority} className="flex items-center gap-1 text-xs text-zinc-500">
            <span className={`h-2 w-2 rounded-full ${l.color}`} />
            {l.priority} ({l.consumers})
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        Global: {globalRps.current.toLocaleString()}/{globalRps.max.toLocaleString()} RPS
      </div>
    </div>
  );
}
