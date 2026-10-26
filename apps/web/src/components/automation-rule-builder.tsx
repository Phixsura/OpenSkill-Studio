"use client";

import { useState } from "react";

interface Condition {
  field: string;
  operator: string;
  value: string;
}

interface Action {
  actionType: string;
  params: Record<string, string>;
}

interface AutomationRule {
  id: string;
  name: string;
  eventType: string;
  logic: "and" | "or";
  conditions: Condition[];
  actions: Action[];
  enabled: boolean;
  executionCount: number;
}

const operators = ["equals", "not_equals", "contains", "greater_than", "less_than", "exists"];
const actionTypes = ["send_notification", "update_status", "call_webhook", "create_ticket", "scale_up", "alert"];

export function AutomationRuleBuilder({
  rules,
  onToggle,
  onDelete,
  onCreate,
}: {
  rules: AutomationRule[];
  onToggle?: (id: string) => void;
  onDelete?: (id: string) => void;
  onCreate?: (rule: { name: string; eventType: string; logic: string }) => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const active = rules.filter((r) => r.enabled).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🤖 Automation Rules</h2>
        <span className="text-sm text-gray-500">{active}/{rules.length} active</span>
      </div>

      <div className="space-y-2">
        {rules.map((rule) => (
          <div key={rule.id} className={`rounded-xl border dark:border-gray-700 overflow-hidden ${!rule.enabled ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between p-3 cursor-pointer"
              onClick={() => setExpanded(expanded === rule.id ? null : rule.id)}>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">{rule.name}</span>
                <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-1.5 py-0.5 rounded">{rule.eventType}</span>
                <span className="text-xs text-gray-400 uppercase">{rule.logic}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">×{rule.executionCount}</span>
                <button onClick={(e) => { e.stopPropagation(); onToggle?.(rule.id); }}
                  className={`text-xs px-2 py-1 rounded ${rule.enabled ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
                  {rule.enabled ? "On" : "Off"}
                </button>
                <button onClick={(e) => { e.stopPropagation(); onDelete?.(rule.id); }}
                  className="text-xs text-red-500">✕</button>
              </div>
            </div>

            {expanded === rule.id && (
              <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
                <div>
                  <span className="text-xs font-semibold text-gray-500">IF ({rule.logic.toUpperCase()})</span>
                  {rule.conditions.map((c, i) => (
                    <div key={i} className="text-xs font-mono ml-3 mt-0.5">
                      {c.field} <span className="text-blue-600">{c.operator}</span> {c.value || "—"}
                    </div>
                  ))}
                </div>
                <div>
                  <span className="text-xs font-semibold text-gray-500">THEN</span>
                  {rule.actions.map((a, i) => (
                    <div key={i} className="text-xs font-mono ml-3 mt-0.5 text-green-600">{a.actionType}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
