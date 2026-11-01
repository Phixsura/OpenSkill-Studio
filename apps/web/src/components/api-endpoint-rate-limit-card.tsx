"use client";

interface RLInfo { method: string; path: string; max_rpm: number; current_count: number; }
interface Props { limits: RLInfo[]; appName: string; }

export default function APIEndpointRateLimitCard({ limits, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Endpoint Limits</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{limits.length} endpoints</span>
      </div>
      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint limits</p>
      ) : (
        <div className="space-y-1">
          {limits.map((l) => {
            const pct = l.max_rpm > 0 ? Math.round((l.current_count / l.max_rpm) * 100) : 0;
            return (
              <div key={`${l.method}-${l.path}`} className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{l.method}</span>
                  <span className="font-mono text-gray-700 dark:text-gray-300">{l.path}</span>
                </div>
                <span className={`${pct >= 90 ? "text-red-500" : "text-gray-400"}`}>{l.current_count}/{l.max_rpm} rpm</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
