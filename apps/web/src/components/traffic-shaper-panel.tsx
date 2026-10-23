"use client";

interface TrafficRule { name: string; target: string; weight: number; pct: number; }
interface TrafficShaperPanelProps { rules: TrafficRule[]; totalWeight: number; }

const COLORS = ["bg-blue-500", "bg-green-500", "bg-yellow-500", "bg-purple-500"];

export function TrafficShaperPanel({ rules, totalWeight }: TrafficShaperPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔀 Traffic Shaping</h3>
      <div className="flex h-5 rounded-full overflow-hidden mb-4">
        {rules.map((r, i) => (
          <div key={r.name} className={`${COLORS[i % COLORS.length]}`}
               style={{ width: `${r.pct}%` }} title={`${r.name}: ${r.pct}%`} />
        ))}
      </div>
      <div className="space-y-2">
        {rules.map((r, i) => (
          <div key={r.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${COLORS[i % COLORS.length]}`} />
              <span className="font-medium">{r.name}</span>
              <span className="text-xs text-gray-400">→ {r.target}</span>
            </div>
            <span className="text-gray-500">{r.pct}% ({r.weight}/{totalWeight})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
