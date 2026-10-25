"use client";

import { useState } from "react";

interface AuditEvent {
  id: string;
  action: string;
  actor: string;
  actorType: "user" | "system" | "extension";
  target: string;
  targetType: string;
  timestamp: string;
  details: Record<string, string>;
}

export function AuditTrailViewer({
  events,
  onLoadMore,
  hasMore,
}: {
  events: AuditEvent[];
  onLoadMore?: () => void;
  hasMore?: boolean;
}) {
  const [filterAction, setFilterAction] = useState("");
  const [filterActor, setFilterActor] = useState("");

  const actions = [...new Set(events.map((e) => e.action))];

  const filtered = events.filter(
    (e) =>
      (!filterAction || e.action === filterAction) &&
      (!filterActor || e.actor.toLowerCase().includes(filterActor.toLowerCase()))
  );

  const actorIcons: Record<string, string> = { user: "👤", system: "🤖", extension: "📦" };

  const actionColors: Record<string, string> = {
    "extension.published": "text-green-500",
    "extension.installed": "text-blue-500",
    "extension.deprecated": "text-orange-500",
    "permission.granted": "text-purple-500",
    "permission.revoked": "text-red-500",
    "key.issued": "text-cyan-500",
    "key.revoked": "text-red-500",
    "config.changed": "text-yellow-500",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📜 Audit Trail</h2>
        <span className="text-sm text-gray-500">{filtered.length} events</span>
      </div>

      <div className="flex gap-2">
        <select
          value={filterAction}
          onChange={(e) => setFilterAction(e.target.value)}
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm"
        >
          <option value="">All actions</option>
          {actions.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
        <input
          type="text"
          value={filterActor}
          onChange={(e) => setFilterActor(e.target.value)}
          placeholder="Filter by actor..."
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm"
        />
      </div>

      <div className="space-y-1">
        {filtered.map((event) => (
          <div key={event.id} className="flex items-start gap-3 py-2 border-b dark:border-gray-800 last:border-0">
            <span className="text-lg mt-0.5">{actorIcons[event.actorType] || "❓"}</span>
            <div className="flex-1 min-w-0">
              <div className="text-sm">
                <span className="font-medium">{event.actor}</span>
                {" "}
                <span className={`font-mono text-xs ${actionColors[event.action] || "text-gray-500"}`}>
                  {event.action}
                </span>
                {" "}
                <span className="text-gray-500">on</span>
                {" "}
                <span className="font-medium">{event.target}</span>
              </div>
              {Object.keys(event.details).length > 0 && (
                <div className="flex gap-2 mt-0.5">
                  {Object.entries(event.details).map(([k, v]) => (
                    <span key={k} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                      {k}: {v}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <span className="text-xs text-gray-400 shrink-0">{event.timestamp}</span>
          </div>
        ))}
      </div>

      {hasMore && onLoadMore && (
        <button onClick={onLoadMore} className="w-full text-center text-sm text-blue-500 py-2">
          Load more events...
        </button>
      )}
    </div>
  );
}
