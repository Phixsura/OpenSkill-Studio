"use client";
interface Breach { service: string; target: number; actual: number; gap: number; severity: string; }
interface SlaBreachPanelProps { breaches: Breach[]; totalServices: number; allMet: boolean; }
const SEV_COLOR: Record<string, string> = { critical: "text-red-600", high: "text-orange-500", warning: "text-yellow-600" };
export function SlaBreachPanel({ breaches, totalServices, allMet }: SlaBreachPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 SLA Breaches</h3>
        <span className={`text-xs font-bold ${allMet ? "text-green-600" : "text-red-500"}`}>
          {allMet ? "✅ All SLA met" : `❌ ${breaches.length} breached`} · {totalServices} services
        </span>
      </div>
      {breaches.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {breaches.map(b => (
            <div key={b.service} className="flex justify-between px-4 py-1.5 text-xs">
              <span className={`font-mono font-bold ${SEV_COLOR[b.severity] ?? ""}`}>{b.service}</span>
              <span className="text-gray-400">{b.actual}% / {b.target}% (gap: {b.gap}%)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
