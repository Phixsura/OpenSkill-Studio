"use client";
interface CheckItem { name: string; status: string; latencyMs: number; }
interface Category { items: CheckItem[]; healthy: number; total: number; allHealthy: boolean; }
interface HcDashboardProps { categories: Record<string, Category>; allHealthy: boolean; healthPct: number; }
const DOT: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500" };
export function HcDashboard({ categories, allHealthy, healthPct }: HcDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-center text-sm font-bold text-white ${allHealthy ? "bg-green-500" : "bg-yellow-500"}`}>
        {allHealthy ? "✅ All Systems Healthy" : `⚠ ${healthPct}% Healthy`}
      </div>
      {Object.entries(categories).map(([cat, data]) => (
        <div key={cat}>
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 text-xs font-semibold flex justify-between">
            <span>{cat}</span>
            <span className={data.allHealthy ? "text-green-600" : "text-yellow-600"}>{data.healthy}/{data.total}</span>
          </div>
          <div className="divide-y dark:divide-gray-700">
            {data.items.map(item => (
              <div key={item.name} className="flex items-center justify-between px-4 py-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${DOT[item.status] ?? "bg-gray-400"}`} />
                  <span>{item.name}</span>
                </div>
                <span className="text-gray-400">{item.latencyMs}ms</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
