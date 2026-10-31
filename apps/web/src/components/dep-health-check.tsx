"use client";

interface DepResult { name: string; type: string; healthy: boolean; latencyMs: number; }
interface DepHealthCheckProps { dependencies: DepResult[]; allOk: boolean;
  healthyCount: number; total: number; }

export function DepHealthCheck({ dependencies, allOk, healthyCount, total }: DepHealthCheckProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Dependencies</h3>
        <span className={`text-xs ${allOk ? "text-green-600" : "text-red-500"}`}>
          {allOk ? "✅ All OK" : `⚠ ${total - healthyCount} failing`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {dependencies.map(d => (
          <div key={d.name} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${d.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{d.name}</span>
              <span className="text-[10px] text-gray-400">{d.type}</span>
            </div>
            <span className="text-xs text-gray-400">{d.latencyMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
