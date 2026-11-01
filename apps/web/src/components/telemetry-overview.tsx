"use client";

interface TopOp { operation: string; count: number; avgMs: number; }
interface TelemetryOverviewProps { totalSpans: number; avgMs: number; p99Ms: number;
  errorRate: number; topOperations: TopOp[]; }

export function TelemetryOverview({ totalSpans, avgMs, p99Ms, errorRate, topOperations }: TelemetryOverviewProps) {
  const maxCount = Math.max(...topOperations.map(o => o.count), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Telemetry</h3>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Spans", v: totalSpans.toLocaleString() }, { l: "Avg", v: `${avgMs}ms` },
          { l: "P99", v: `${p99Ms}ms` }, { l: "Errors", v: `${errorRate}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-4 space-y-2">
        {topOperations.map(op => (
          <div key={op.operation}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{op.operation}</span>
              <span className="text-gray-400">{op.count} · {op.avgMs}ms</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(op.count / maxCount) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
