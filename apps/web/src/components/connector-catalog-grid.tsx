"use client";
import { useState } from "react";

interface Connector { connectorId: string; name: string; provider: string; category: string; icon: string; installedCount: number; status: string; }

const catIcons: Record<string, string> = { crm: "👥", analytics: "📊", storage: "💾", communication: "💬", payment: "💳", dev: "🛠️" };

export function ConnectorCatalogGrid({ connectors, onInstall }: { connectors: Connector[]; onInstall?: (id: string) => void }) {
  const [filter, setFilter] = useState("");
  const cats = [...new Set(connectors.map(c => c.category))];
  const filtered = filter ? connectors.filter(c => c.category === filter) : connectors;

  return (
    <div className="space-y-3">
      <div className="flex gap-1 flex-wrap">
        <button onClick={() => setFilter("")} className={`text-xs px-3 py-1 rounded-full ${!filter ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {cats.map(c => (
          <button key={c} onClick={() => setFilter(c)} className={`text-xs px-3 py-1 rounded-full capitalize ${filter === c ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {catIcons[c] || "🔌"} {c}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {filtered.map(c => (
          <div key={c.connectorId} className="border dark:border-gray-700 rounded-xl p-3 flex items-start gap-3">
            <span className="text-2xl">{c.icon}</span>
            <div className="flex-1 min-w-0">
              <span className="font-medium text-sm block">{c.name}</span>
              <span className="text-xs text-gray-500">{c.provider} · {c.installedCount} installs</span>
              {c.status === "beta" && <span className="text-xs bg-yellow-100 text-yellow-700 px-1.5 rounded ml-1">beta</span>}
            </div>
            <button onClick={() => onInstall?.(c.connectorId)} className="text-xs bg-blue-500 text-white px-2 py-1 rounded-lg shrink-0">Install</button>
          </div>
        ))}
      </div>
    </div>
  );
}
