"use client";
interface SvcConcurrency { service: string; active: number; limit: number; }
interface ConcurrencyLimPanelProps { services: SvcConcurrency[]; rejected: number; }
export function ConcurrencyLimPanel({ services, rejected }: ConcurrencyLimPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Concurrency Limiter</h3>
        <span className="text-xs text-gray-400">{services.length} services · {rejected} rejected</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{s.service}</span>
              <span className={`${s.active >= s.limit ? "text-red-500 font-bold" : "text-gray-400"}`}>{s.active}/{s.limit}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${s.active >= s.limit ? "bg-red-500" : "bg-blue-500"}`}
                style={{ width: `${s.active / Math.max(s.limit, 1) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
