"use client";

interface Rule { name: string; triggerEvent: string; actionType: string; enabled: boolean; }
interface AutomationRulesListProps { rules: Rule[]; canAdd: boolean; onAdd?: () => void; }

export function AutomationRulesList({ rules, canAdd, onAdd }: AutomationRulesListProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">⚡ Automation Rules ({rules.length})</h4>
        {canAdd && onAdd && <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">+ Add Rule</button>}
      </div>
      {rules.length === 0 ? <p className="text-sm text-gray-400">No automation rules</p> : (
        <ul className="space-y-2">{rules.map(r => (
          <li key={r.name} className={`rounded border p-2 text-sm ${r.enabled ? "border-green-200" : "border-gray-200 opacity-60"}`}>
            <span className="font-medium">{r.name}</span>
            <span className="ml-2 text-xs text-gray-500">{r.triggerEvent} → {r.actionType}</span>
          </li>
        ))}</ul>
      )}
    </div>
  );
}
