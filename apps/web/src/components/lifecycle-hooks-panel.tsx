"use client";

import { useState } from "react";

interface LifecycleHook {
  hookId: string;
  event: string;
  handlerName: string;
  order: number;
  enabled: boolean;
  executionCount: number;
  errorCount: number;
  lastError?: string;
}

const eventIcons: Record<string, string> = {
  before_start: "⏳", after_start: "🟢", before_stop: "⏸",
  after_stop: "🔴", on_crash: "💥", on_restart: "🔄", on_health_check: "💓",
};

export function LifecycleHooksPanel({
  hooks,
  onTrigger,
  onToggle,
  onRemove,
}: {
  hooks: LifecycleHook[];
  onTrigger?: (event: string) => void;
  onToggle?: (hookId: string) => void;
  onRemove?: (hookId: string) => void;
}) {
  const events = [...new Set(hooks.map((h) => h.event))].sort();
  const [eventFilter, setEventFilter] = useState<string>("all");
  const filtered = eventFilter === "all" ? hooks : hooks.filter((h) => h.event === eventFilter);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔗 Lifecycle Hooks</h2>

      <div className="flex gap-1 flex-wrap">
        <button onClick={() => setEventFilter("all")}
          className={`text-xs px-2.5 py-1 rounded-full ${eventFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          All ({hooks.length})
        </button>
        {events.map((evt) => (
          <button key={evt} onClick={() => setEventFilter(evt)}
            className={`text-xs px-2.5 py-1 rounded-full ${eventFilter === evt ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {eventIcons[evt] || "📌"} {evt}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((hook) => (
          <div key={hook.hookId} className={`rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between ${!hook.enabled ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span>{eventIcons[hook.event] || "📌"}</span>
              <code className="text-sm">{hook.handlerName}</code>
              <span className="text-xs text-gray-400">#{hook.order}</span>
              <span className="text-xs text-gray-400">×{hook.executionCount}</span>
              {hook.errorCount > 0 && (
                <span className="text-xs text-red-500">{hook.errorCount} errors</span>
              )}
            </div>
            <div className="flex gap-1">
              <button onClick={() => onToggle?.(hook.hookId)}
                className={`text-xs px-2 py-0.5 rounded ${hook.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                {hook.enabled ? "On" : "Off"}
              </button>
              <button onClick={() => onRemove?.(hook.hookId)} className="text-xs text-red-500">✕</button>
            </div>
          </div>
        ))}
      </div>

      {events.length > 0 && (
        <div>
          <span className="text-xs text-gray-500">Trigger event:</span>
          <div className="flex gap-1 mt-1">
            {events.map((evt) => (
              <button key={evt} onClick={() => onTrigger?.(evt)}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                {eventIcons[evt]} {evt}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
