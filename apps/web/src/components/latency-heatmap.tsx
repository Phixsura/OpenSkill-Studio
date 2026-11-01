"use client";

interface LatencyPair { pair: string; avgMs: number; p99Ms: number; samples: number; }
interface LatencyHeatmapProps { pairs: LatencyPair[]; totalPairs: number;
  highestLatency: string | null; }

export function LatencyHeatmap({ pairs, totalPairs, highestLatency }: LatencyHeatmapProps) {
  const maxAvg = Math.max(...pairs.map(p => p.avgMs), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 Network Latency</h3>
        <span className="text-xs text-gray-400">{totalPairs} pairs{highestLatency ? ` · slowest: ${highestLatency}` : ""}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pairs.map(p => {
          const pct = (p.avgMs / maxAvg) * 100;
          const color = p.avgMs > 50 ? "bg-red-500" : p.avgMs > 10 ? "bg-yellow-500" : "bg-green-500";
          return (
            <div key={p.pair} className="px-4 py-2">
              <div className="flex justify-between text-xs mb-0.5">
                <span className="font-mono">{p.pair}</span>
                <span className="text-gray-400">avg {p.avgMs}ms · p99 {p.p99Ms}ms · {p.samples} samples</span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
