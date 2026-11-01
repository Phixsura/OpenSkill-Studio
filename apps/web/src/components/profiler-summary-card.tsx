"use client";

interface ProfilerSummaryCardProps { total: number; avgMs: number; p95Ms: number; slowestFn: string | null; fastestFn: string | null; fnCount: number; }

export function ProfilerSummaryCard({ total, avgMs, p95Ms, slowestFn, fastestFn, fnCount }: ProfilerSummaryCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">⚡ Execution Profile</h4>
      <div className="grid grid-cols-3 gap-3 text-center text-sm">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-500">Total</p></div>
        <div><p className="text-lg font-bold">{avgMs}ms</p><p className="text-xs text-gray-500">Avg</p></div>
        <div><p className="text-lg font-bold">{p95Ms}ms</p><p className="text-xs text-gray-500">P95</p></div>
      </div>
      {(slowestFn || fastestFn) && (
        <div className="mt-3 space-y-1 text-sm">
          {fastestFn && <p>🚀 Fastest: <code className="text-xs">{fastestFn}</code></p>}
          {slowestFn && <p>🐢 Slowest: <code className="text-xs">{slowestFn}</code></p>}
          <p className="text-xs text-gray-400">{fnCount} functions profiled</p>
        </div>
      )}
    </div>
  );
}
