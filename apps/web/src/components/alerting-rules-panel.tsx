"use client";

interface AlertRule { rule_id: string; name: string; condition: string; status: string; notify_channels: string[]; }
interface AlertingRulesPanelProps { rules: AlertRule[]; onToggle: (id: string) => void;
  onDelete: (id: string) => void; onCreate: () => void; }

export function AlertingRulesPanel({ rules, onToggle, onDelete, onCreate }: AlertingRulesPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Alert Rules</h2>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">New Rule</button>
      </div>
      {rules.map(r => (
        <div key={r.rule_id} className="rounded-lg border p-3 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <span className="font-medium">{r.name}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs ${r.status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
              {r.status}
            </span>
          </div>
          <p className="mt-1 font-mono text-xs text-gray-400">{r.condition}</p>
          <div className="mt-2 flex items-center justify-between">
            <div className="flex gap-1">
              {r.notify_channels.map(c => (
                <span key={c} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{c}</span>
              ))}
            </div>
            <div className="flex gap-2">
              <button onClick={() => onToggle(r.rule_id)} className="text-xs text-blue-500">
                {r.status === "active" ? "Mute" : "Enable"}
              </button>
              <button onClick={() => onDelete(r.rule_id)} className="text-xs text-red-500">Delete</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
