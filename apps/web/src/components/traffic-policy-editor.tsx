"use client";

interface PolicyRule { match: string; action: string; priority: number;
  rateLimit: number; timeoutMs: number; }
interface TrafficPolicyEditorProps { name: string; rules: PolicyRule[];
  onAddRule: () => void; onDeleteRule: (idx: number) => void; }

export function TrafficPolicyEditor({ name, rules, onAddRule, onDeleteRule }: TrafficPolicyEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 {name}</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          <button onClick={onAddRule} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Rule</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-gray-400">#{r.priority}</span>
              <span className="font-mono">{r.match}</span>
              <span className={`px-1.5 py-0.5 rounded ${r.action === "allow" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{r.action}</span>
            </div>
            <div className="flex gap-2 text-gray-400">
              {r.rateLimit > 0 && <span>{r.rateLimit} rpm</span>}
              <span>{r.timeoutMs}ms</span>
              <button onClick={() => onDeleteRule(i)} className="text-red-500">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
