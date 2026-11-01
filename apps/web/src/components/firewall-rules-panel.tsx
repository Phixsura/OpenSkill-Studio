"use client";

interface FirewallRule { name: string; direction: string; action: string;
  protocol: string; port: number; source: string; }
interface FirewallRulesPanelProps { rules: FirewallRule[]; allowCount: number;
  denyCount: number; onAdd: () => void; }

export function FirewallRulesPanel({ rules, allowCount, denyCount, onAdd }: FirewallRulesPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Firewall Rules</h3>
        <div className="flex gap-2">
          <span className="text-xs text-green-600">{allowCount} allow</span>
          <span className="text-xs text-red-500">{denyCount} deny</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Rule</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 rounded ${r.action === "allow" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{r.action}</span>
              <span className="text-gray-400">{r.direction}</span>
              <span className="font-mono">{r.protocol.toUpperCase()}:{r.port}</span>
            </div>
            <span className="font-mono text-gray-400">{r.source}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
