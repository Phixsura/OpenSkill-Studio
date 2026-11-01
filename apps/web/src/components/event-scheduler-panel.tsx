"use client";

import { useState } from "react";

interface ScheduledEvent {
  id: string;
  name: string;
  action: string;
  scheduleType: "once" | "recurring" | "interval";
  status: "active" | "paused" | "completed" | "failed" | "cancelled";
  intervalSeconds: number;
  runCount: number;
  maxRuns: number;
  failureCount: number;
  nextRunAt?: string;
  lastRunAt?: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "▶" },
  paused: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏸" },
  completed: { color: "bg-blue-100 text-blue-600 dark:bg-blue-900/30", icon: "✓" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "✗" },
  cancelled: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800", icon: "⊘" },
};

function formatInterval(seconds: number): string {
  if (seconds >= 86400) return `${Math.floor(seconds / 86400)}d`;
  if (seconds >= 3600) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 60)}m`;
}

export function EventSchedulerPanel({
  events,
  onPause,
  onResume,
  onCancel,
}: {
  events: ScheduledEvent[];
  onPause?: (id: string) => void;
  onResume?: (id: string) => void;
  onCancel?: (id: string) => void;
}) {
  const active = events.filter((e) => e.status === "active").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⏰ Event Scheduler</h2>
        <span className="text-sm text-gray-500">{active} active</span>
      </div>

      <div className="space-y-2">
        {events.map((ev) => {
          const cfg = statusConfig[ev.status];
          return (
            <div key={ev.id} className="rounded-xl border dark:border-gray-700 p-3">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{ev.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{ev.status}</span>
                  <span className="text-xs text-gray-400">{ev.scheduleType}</span>
                </div>
                <div className="flex gap-1">
                  {ev.status === "active" && (
                    <button onClick={() => onPause?.(ev.id)}
                      className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Pause</button>
                  )}
                  {ev.status === "paused" && (
                    <button onClick={() => onResume?.(ev.id)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Resume</button>
                  )}
                  {(ev.status === "active" || ev.status === "paused") && (
                    <button onClick={() => onCancel?.(ev.id)}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Cancel</button>
                  )}
                </div>
              </div>
              <div className="flex gap-3 text-xs text-gray-500">
                <span>Action: <code>{ev.action}</code></span>
                {ev.scheduleType === "recurring" && <span>Every {formatInterval(ev.intervalSeconds)}</span>}
                <span>Runs: {ev.runCount}{ev.maxRuns > 0 ? `/${ev.maxRuns}` : ""}</span>
                {ev.failureCount > 0 && <span className="text-red-500">{ev.failureCount} failures</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
