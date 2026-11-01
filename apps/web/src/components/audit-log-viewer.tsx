"use client";

import { useState } from "react";

interface AuditEvent { id: string; action: string; actor: string; target: string;
  severity: string; icon: string; ip: string; timestamp: string; }
interface AuditLogViewerProps { events: AuditEvent[]; bySeverity: Record<string, number>; }

const sevColors: Record<string, string> = {
  info: "text-blue-600", warning: "text-yellow-600", critical: "text-red-600",
};

export function AuditLogViewer({ events, bySeverity }: AuditLogViewerProps) {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? events : events.filter(e => e.severity === filter);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Audit Log</h3>
        <div className="flex gap-1">
          {["all", "info", "warning", "critical"].map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={`rounded px-2 py-0.5 text-xs capitalize ${filter === s ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
              {s}{s !== "all" && bySeverity[s] ? ` (${bySeverity[s]})` : ""}
            </button>
          ))}
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-72 overflow-y-auto">
        {filtered.map(e => (
          <div key={e.id} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{e.icon}</span>
                <span className={`text-sm font-medium ${sevColors[e.severity] ?? ""}`}>{e.action}</span>
              </div>
              <time className="text-xs text-gray-400">{new Date(e.timestamp).toLocaleString()}</time>
            </div>
            <p className="mt-0.5 text-xs text-gray-500">by {e.actor} · {e.ip}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
