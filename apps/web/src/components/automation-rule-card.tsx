"use client";

interface Condition {
  field: string;
  op: string;
  value: string | null;
}

interface Action {
  action_type: "webhook" | "notification" | "set_field" | "log";
  config: Record<string, string>;
}

interface AutomationRule {
  rule_id: string;
  name: string;
  event_type: string;
  conditions: Condition[];
  logic: "and" | "or";
  actions: Action[];
  enabled: boolean;
  last_triggered?: string | null;
  match_count?: number;
}

interface AutomationRuleCardProps {
  rule: AutomationRule;
  onToggle: (ruleId: string, enabled: boolean) => void;
  onDelete: (ruleId: string) => void;
  onTest: (ruleId: string) => void;
}

const OP_LABELS: Record<string, string> = {
  equals: "=",
  not_equals: "≠",
  contains: "contains",
  regex: "matches",
  exists: "exists",
  gt: ">",
  lt: "<",
  gte: "≥",
  lte: "≤",
};

const ACTION_ICONS: Record<string, string> = {
  webhook: "🌐",
  notification: "🔔",
  set_field: "✏️",
  log: "📝",
};

const ACTION_LABELS: Record<string, string> = {
  webhook: "Webhook",
  notification: "Notification",
  set_field: "Set Field",
  log: "Log",
};

function ConditionChip({
  condition,
  isLast,
  logic,
}: {
  condition: Condition;
  isLast: boolean;
  logic: string;
}) {
  const op = OP_LABELS[condition.op] ?? condition.op;
  return (
    <span className="inline-flex items-center gap-1">
      <code className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium dark:bg-blue-900/20">
        {condition.field}
      </code>
      <span className="text-[10px] text-gray-500">{op}</span>
      {condition.value !== null && condition.op !== "exists" && (
        <code className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">
          {condition.value}
        </code>
      )}
      {!isLast && (
        <span className="mx-1 rounded bg-purple-100 px-1 py-0.5 text-[10px] font-bold text-purple-700 dark:bg-purple-900/20 dark:text-purple-300">
          {logic.toUpperCase()}
        </span>
      )}
    </span>
  );
}

export function AutomationRuleCard({ rule, onToggle, onDelete, onTest }: AutomationRuleCardProps) {
  return (
    <div
      className={`rounded-lg border p-4 ${rule.enabled ? "border-gray-200 dark:border-gray-700" : "border-gray-200 bg-gray-50 opacity-60 dark:border-gray-700 dark:bg-gray-800/30"}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => onToggle(rule.rule_id, !rule.enabled)}
            className={`relative h-5 w-9 rounded-full transition-colors ${rule.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}
            role="switch"
            aria-checked={rule.enabled}
            aria-label={`Toggle ${rule.name}`}
          >
            <span
              className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${rule.enabled ? "left-[18px]" : "left-0.5"}`}
            />
          </button>
          <h4 className="text-sm font-semibold">{rule.name}</h4>
        </div>
        <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] text-gray-500 dark:bg-gray-800">
          {rule.event_type}
        </span>
      </div>

      {/* Conditions */}
      <div className="mt-2 flex flex-wrap items-center gap-1">
        <span className="mr-1 text-[10px] font-semibold uppercase text-gray-400">IF</span>
        {rule.conditions.map((c, i) => (
          <ConditionChip
            key={i}
            condition={c}
            isLast={i === rule.conditions.length - 1}
            logic={rule.logic}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="mt-2 flex flex-wrap items-center gap-1.5">
        <span className="mr-1 text-[10px] font-semibold uppercase text-gray-400">THEN</span>
        {rule.actions.map((a, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-1 rounded bg-green-50 px-1.5 py-0.5 text-[10px] text-green-700 dark:bg-green-900/20 dark:text-green-300"
          >
            <span>{ACTION_ICONS[a.action_type] ?? "⚡"}</span>
            {ACTION_LABELS[a.action_type] ?? a.action_type}
          </span>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-3 flex items-center justify-between border-t border-gray-100 pt-2 dark:border-gray-800">
        <div className="text-[10px] text-gray-400">
          {rule.match_count !== undefined && <span>{rule.match_count} matches</span>}
          {rule.last_triggered && <span className="ml-2">Last: {rule.last_triggered}</span>}
        </div>
        <div className="flex gap-1.5">
          <button
            onClick={() => onTest(rule.rule_id)}
            className="rounded border border-blue-300 px-2 py-0.5 text-[10px] text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400"
          >
            Dry Run
          </button>
          <button
            onClick={() => onDelete(rule.rule_id)}
            className="rounded border border-red-300 px-2 py-0.5 text-[10px] text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
