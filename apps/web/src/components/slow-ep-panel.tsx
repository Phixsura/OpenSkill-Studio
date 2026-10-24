"use client";
interface SlowEp { endpoint: string; avgMs: number; p99Ms: number; samples: number; }
interface SlowEpPanelProps { slowEndpoints: SlowEp[]; totalEndpoints: number; thresholdMs: number; }
export function SlowEpPanel({ slowEndpoints, totalEndpoints, thresholdMs }: SlowEpPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐌 Slow Endpoints</h3>
        <span className={`text-xs ${slowEndpoints.length > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {slowEndpoints.length}/{totalEndpoints} slow (p99 {">"}{thresholdMs}ms)
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {slowEndpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <span className="text-yellow-600">avg {e.avgMs}ms · p99 {e.p99Ms}ms · {e.samples} reqs</span>
          </div>
        ))}
        {slowEndpoints.length === 0 && <div className="px-4 py-3 text-xs text-green-600 text-center">All endpoints fast</div>}
      </div>
    </div>
  );
}
