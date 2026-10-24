"use client";
interface LatPair { source: string; destination: string; avgMs: number; p99Ms: number; samples: number; }
interface NetLatencyPanelProps { pairs: LatPair[]; totalMeasurements: number; }
export function NetLatencyPanel({ pairs, totalMeasurements }: NetLatencyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 Network Latency</h3>
        <span className="text-xs text-gray-400">{pairs.length} pairs · {totalMeasurements.toLocaleString()} measurements</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pairs.map(p => (
          <div key={`${p.source}→${p.destination}`} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.source} → {p.destination}</span>
            <span className="text-gray-400">avg {p.avgMs}ms · p99 {p.p99Ms}ms · {p.samples} samples</span>
          </div>
        ))}
      </div>
    </div>
  );
}
