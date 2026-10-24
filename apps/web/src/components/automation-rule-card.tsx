"use client";

interface AutomationRuleCardProps {
  name: string;
  triggerEvent: string;
  actionType: string;
  enabled: boolean;
  executionsPerHour?: number;
  onToggle?: (enabled: boolean) => void;
  onDelete?: () => void;
}

const ACTION_ICONS: Record<string, string> = {
  webhook: "🌐",
  sandbox_function: "📦",
  api_call: "🔗",
  notification: "🔔",
};

export function AutomationRuleCard({
  name, triggerEvent, actionType, enabled, executionsPerHour, onToggle, onDelete,
}: AutomationRuleCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${enabled ? "border-green-200 dark:border-green-800" : "border-gray-200 opacity-60 dark:border-gray-700"}`}>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold">{name}</h4>
        <div className="flex items-center gap-2">
          {onToggle && (
            <button
              onClick={() => onToggle(!enabled)}
              className={`rounded-full px-2 py-0.5 text-xs ${enabled ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" : "bg-gray-100 text-gray-600 dark:bg-gray-800"}`}
            >
              {enabled ? "Active" : "Disabled"}
            </button>
          )}
          {onDelete && (
            <button onClick={onDelete} className="text-xs text-red-500 hover:text-red-700">Delete</button>
          )}
        </div>
      </div>
      <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
        <p>🎯 Trigger: <span className="font-mono text-xs">{triggerEvent}</span></p>
        <p>{ACTION_ICONS[actionType] ?? "⚡"} Action: {actionType.replace(/_/g, " ")}</p>
        {executionsPerHour != null && (
          <p className="text-xs">Rate limit: {executionsPerHour}/hour</p>
        )}
      </div>
    </div>
  );
}
