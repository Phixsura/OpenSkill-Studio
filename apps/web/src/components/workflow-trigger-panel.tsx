"use client";

import { useState } from "react";

interface TriggerCondition {
  field: string;
  operator: string;
  value: string;
}

interface WorkflowTrigger {
  id: string;
  name: string;
  type: "webhook" | "cron" | "manual" | "event";
  status: "active" | "paused" | "disabled";
  conditions: TriggerCondition[];
  cronExpression?: string;
  eventType?: string;
  fireCount: number;
  lastFired?: string;
}

const typeIcons: Record<string, string> = {
  webhook: "🔗", cron: "⏰", manual: "👆", event: "⚡",
};

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  paused: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
  disabled: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

export function WorkflowTriggerPanel({
  triggers,
  workflowName,
  onToggle,
  onFire,
}: {
  triggers: WorkflowTrigger[];
  workflowName: string;
  onToggle?: (id: string) => void;
  onFire?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-bold">⚙️ {workflowName} Triggers</h2>
      {triggers.length === 0 && (
        <p className="text-sm text-gray-500">No triggers configured.</p>
      )}
      {triggers.map((t) => (
        <div key={t.id} className="rounded-xl border dark:border-gray-700 overflow-hidden">
          <div className="flex items-center gap-3 p-3 cursor-pointer"
               onClick={() => setExpanded(expanded === t.id ? null : t.id)}>
            <span className="text-xl">{typeIcons[t.type]}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{t.name}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${statusColors[t.status]}`}>
                  {t.status}
                </span>
                <span className="text-xs text-gray-400">{t.type}</span>
              </div>
              <span className="text-xs text-gray-500">
                Fired {t.fireCount}x{t.lastFired ? ` · Last: ${t.lastFired}` : ""}
              </span>
            </div>
            <div className="flex gap-1">
              {t.type === "manual" && t.status === "active" && (
                <button onClick={(e) => { e.stopPropagation(); onFire?.(t.id); }}
                  className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                  Fire
                </button>
              )}
              <button onClick={(e) => { e.stopPropagation(); onToggle?.(t.id); }}
                className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {t.status === "active" ? "Pause" : "Resume"}
              </button>
            </div>
          </div>
          {expanded === t.id && (
            <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
              {t.cronExpression && (
                <div className="text-xs"><span className="text-gray-500">Cron:</span> <code>{t.cronExpression}</code></div>
              )}
              {t.eventType && (
                <div className="text-xs"><span className="text-gray-500">Event:</span> {t.eventType}</div>
              )}
              {t.conditions.length > 0 && (
                <div>
                  <span className="text-xs text-gray-500">Conditions:</span>
                  {t.conditions.map((c, i) => (
                    <div key={i} className="text-xs font-mono ml-2">
                      {c.field} {c.operator} {c.value}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
