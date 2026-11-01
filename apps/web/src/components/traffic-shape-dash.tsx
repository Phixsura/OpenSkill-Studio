"use client";

interface TrafficEntry { key: string; current: number; limit: number; remaining: number; allowed: boolean; }
interface TrafficShapeDashProps { trackedKeys: number; maxRequests: number;
  windowSeconds: number; entries: TrafficEntry[]; }

export function TrafficShapeDash({ trackedKeys, maxRequests, windowSeconds, entries }: TrafficShapeDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Traffic Shaping</h3>
        <span className="text-xs text-gray-400">{trackedKeys} keys · {maxRequests}/{windowSeconds}s</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.key} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{e.key}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{e.current}/{e.limit}</span>
              <span className={`w-2 h-2 rounded-full ${e.remaining > 0 ? "bg-green-500" : "bg-red-500"}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
