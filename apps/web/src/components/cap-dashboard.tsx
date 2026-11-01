"use client";

interface Critical { name: string; type: string; pct: number; }
interface CapDashboardProps { overallPct: number; status: string;
  criticalCount: number; critical: Critical[]; resourceCount: number; }

export function CapDashboard({ overallPct, status, criticalCount, critical, resourceCount }: CapDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Capacity</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{overallPct}%</span>
          <span className={status === "healthy" ? "text-green-600" : "text-red-500"}>
            {status === "healthy" ? "✅ Healthy" : `⚠ ${criticalCount} critical`}
          </span>
        </div>
      </div>
      {critical.length > 0 && (
        <div className="p-3 bg-red-50 dark:bg-red-900/10">
          {critical.map(c => (
            <div key={c.name} className="text-xs text-red-600">⚠ {c.name} ({c.type}): {c.pct}%</div>
          ))}
        </div>
      )}
    </div>
  );
}
