"use client";

import { useState } from "react";

interface ChangeRecord { changeId: string; changeType: string; description: string; actor: string; timestamp: string; hasDiff: boolean; }

const typeIcons: Record<string, string> = {
  config: "⚙️", deploy: "🚀", permission: "🔐", setting: "📝", code: "💻",
};

export function ChangeHistoryPanel({
  changes, changeTypes, actors, onFilter,
}: {
  changes: ChangeRecord[]; changeTypes: string[]; actors: string[];
  onFilter?: (type: string | null, actor: string | null) => void;
}) {
  const [typeFilter, setTypeFilter] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📜 Change History</h2>
      <div className="flex gap-1 flex-wrap">
        <button onClick={() => { setTypeFilter(null); onFilter?.(null, null); }}
          className={`text-xs px-2.5 py-1 rounded-full ${!typeFilter ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>All</button>
        {changeTypes.map((t) => (
          <button key={t} onClick={() => { setTypeFilter(t); onFilter?.(t, null); }}
            className={`text-xs px-2.5 py-1 rounded-full ${typeFilter === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {typeIcons[t] || "●"} {t}
          </button>
        ))}
      </div>
      <div className="space-y-1">
        {changes.map((c) => (
          <div key={c.changeId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm">
            <span>{typeIcons[c.changeType] || "●"}</span>
            <span className="flex-1">{c.description}</span>
            <span className="text-xs text-gray-400">{c.actor} · {c.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
