"use client";

interface MeshConnection { source: string; destination: string; requests: number;
  errors: number; avgLatencyMs: number; errorRatePct: number; }
interface MeshTelemetryViewProps { connections: MeshConnection[];
  totalRequests: number; meshErrorRate: number; uniquePairs: number; }

export function MeshTelemetryView({ connections, totalRequests, meshErrorRate, uniquePairs }: MeshTelemetryViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Mesh Telemetry</h3>
        <span className="text-xs text-gray-400">{uniquePairs} pairs · {totalRequests} req · {meshErrorRate}% errors</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {connections.map(c => (
          <div key={`${c.source}→${c.destination}`} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{c.source} → {c.destination}</span>
            <div className="flex gap-3 text-gray-400">
              <span>{c.requests} req</span>
              <span>{c.avgLatencyMs}ms</span>
              <span className={c.errorRatePct > 1 ? "text-red-500" : ""}>{c.errorRatePct}% err</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
