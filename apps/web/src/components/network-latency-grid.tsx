"use client";

interface Region { id: string; label: string; }
interface Edge { from: string; to: string; latency_ms: number; quality: string; }
interface NetworkLatencyGridProps { regions: Region[]; edges: Edge[]; userRegion?: string; }

const qualityColor: Record<string, string> = {
  good: "text-green-600", fair: "text-yellow-600", poor: "text-red-600",
};

export function NetworkLatencyGrid({ regions, edges, userRegion }: NetworkLatencyGridProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Network Latency</h2>
      <div className="grid gap-2 sm:grid-cols-2">
        {edges.map(e => (
          <div key={`${e.from}-${e.to}`} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-1 text-sm">
              <span className={e.from === userRegion ? "font-bold text-blue-600" : ""}>
                {regions.find(r => r.id === e.from)?.label ?? e.from}
              </span>
              <span className="text-gray-300">↔</span>
              <span className={e.to === userRegion ? "font-bold text-blue-600" : ""}>
                {regions.find(r => r.id === e.to)?.label ?? e.to}
              </span>
            </div>
            <span className={`font-mono text-sm font-bold ${qualityColor[e.quality] ?? ""}`}>{e.latency_ms}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
