"use client";
interface FaultRule { source: string; destination: string; faultType: string; percentage: number; active: boolean; }
interface MeshFaultPanelProps { rules: FaultRule[]; activeCount: number; }
export function MeshFaultPanel({ rules, activeCount }: MeshFaultPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💉 Mesh Fault Injection</h3>
        <span className={`text-xs ${activeCount > 0 ? "text-red-500" : "text-green-600"}`}>
          {activeCount > 0 ? `⚠ ${activeCount} active` : "✅ No faults"} · {rules.length} rules
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map((r, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.source} → {r.destination}</span>
            <span className={r.active ? "text-red-500" : "text-gray-400"}>
              {r.faultType} {r.percentage}%{r.active ? " ACTIVE" : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
