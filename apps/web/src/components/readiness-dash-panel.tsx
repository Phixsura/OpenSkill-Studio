"use client";
interface SvcReadiness { service: string; score: number; total: number; ready: boolean; }
interface ReadinessDashPanelProps { services: SvcReadiness[]; readyCount: number; notReady: number; readinessPct: number; }
export function ReadinessDashPanel({ services, readyCount, notReady, readinessPct }: ReadinessDashPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Production Readiness</h3>
        <span className={`text-xs font-bold ${readinessPct >= 100 ? "text-green-600" : "text-yellow-600"}`}>
          {readinessPct}% ready · {readyCount} ready · {notReady} not ready
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{s.ready ? "✅" : "⚠️"}</span>
              <span className="font-mono">{s.service}</span>
            </div>
            <span className="text-gray-400">{s.score}/{s.total}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
