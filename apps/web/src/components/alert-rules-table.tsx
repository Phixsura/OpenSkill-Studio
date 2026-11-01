"use client";

interface AlertRule { name: string; metric: string; operator: string; threshold: number;
  severity: string; enabled: boolean; }
interface TriggeredAlert { rule: string; severity: string; message: string; }
interface AlertRulesTableProps { rules: AlertRule[]; triggered: TriggeredAlert[];
  onToggle: (name: string) => void; }

const SEV_STYLE: Record<string, string> = {
  critical: "bg-red-100 text-red-700", warning: "bg-yellow-100 text-yellow-700", info: "bg-blue-100 text-blue-700",
};

export function AlertRulesTable({ rules, triggered, onToggle }: AlertRulesTableProps) {
  const triggeredNames = new Set(triggered.map(t => t.rule));
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 Alert Rules</h3>
        {triggered.length > 0 && (
          <span className="text-xs text-red-500 font-medium">{triggered.length} firing</span>
        )}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map(r => (
          <div key={r.name} className={`flex items-center justify-between px-4 py-3 ${triggeredNames.has(r.name) ? "bg-red-50 dark:bg-red-900/10" : ""}`}>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{r.name}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${SEV_STYLE[r.severity] || ""}`}>{r.severity}</span>
                {triggeredNames.has(r.name) && <span className="text-xs text-red-500">🔔 Firing</span>}
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{r.metric} {r.operator} {r.threshold}</p>
            </div>
            <button onClick={() => onToggle(r.name)}
              className={`w-9 h-5 rounded-full transition ${r.enabled ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"}`}>
              <span className={`block w-3.5 h-3.5 rounded-full bg-white transition transform ${r.enabled ? "translate-x-4" : "translate-x-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
