"use client";

interface Dep { name: string; status: string; latencyMs?: number; }
interface DepHealthViewProps { deps: Dep[]; healthPct: number; allHealthy: boolean; }

const STATUS_ICONS: Record<string, string> = { healthy: "🟢", degraded: "🟡", down: "🔴" };

export function DepHealthView({ deps, healthPct, allHealthy }: DepHealthViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Dependency Health</h3>
        <span className={`text-xs ${allHealthy ? "text-green-600" : "text-yellow-600"}`}>
          {healthPct}% healthy
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {deps.map(d => (
          <div key={d.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <span>{STATUS_ICONS[d.status] ?? "⚪"} {d.name}</span>
            <span className="text-gray-400 capitalize">{d.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
