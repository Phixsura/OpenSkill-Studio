"use client";

import { useState } from "react";

interface NotificationChannel {
  id: string;
  name: string;
  type: "email" | "slack" | "webhook" | "in_app";
  enabled: boolean;
  minSeverity: "info" | "warning" | "error" | "critical";
  eventFilters: string[];
  deliveredCount: number;
  failedCount: number;
}

const typeIcons: Record<string, string> = {
  email: "📧", slack: "💬", webhook: "🔗", in_app: "🔔",
};

const severityColors: Record<string, string> = {
  info: "text-blue-600", warning: "text-yellow-600",
  error: "text-red-600", critical: "text-red-800",
};

export function NotificationChannelManager({
  channels,
  extensionName,
  onToggle,
  onDelete,
}: {
  channels: NotificationChannel[];
  extensionName: string;
  onToggle?: (id: string) => void;
  onDelete?: (id: string) => void;
}) {
  const enabled = channels.filter((c) => c.enabled).length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔔 {extensionName} Notifications</h2>
        <span className="text-sm text-gray-500">{enabled}/{channels.length} active</span>
      </div>

      {channels.map((ch) => (
        <div key={ch.id}
          className={`rounded-xl border dark:border-gray-700 p-4 ${!ch.enabled ? "opacity-50" : ""}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg">{typeIcons[ch.type]}</span>
              <span className="font-semibold text-sm">{ch.name}</span>
              <span className="text-xs text-gray-400">{ch.type}</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => onToggle?.(ch.id)}
                className={`text-xs px-2 py-1 rounded ${ch.enabled ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
                {ch.enabled ? "On" : "Off"}
              </button>
              <button onClick={() => onDelete?.(ch.id)}
                className="text-xs text-red-500 hover:text-red-700">✕</button>
            </div>
          </div>
          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
            <span>Min: <span className={severityColors[ch.minSeverity]}>{ch.minSeverity}</span></span>
            <span>✓ {ch.deliveredCount}</span>
            {ch.failedCount > 0 && <span className="text-red-500">✗ {ch.failedCount}</span>}
            {ch.eventFilters.length > 0 && (
              <span>Filters: {ch.eventFilters.join(", ")}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
