"use client";
interface LagPair { source: string; destination: string; avgMs: number; maxMs: number; calls: number; }
interface DepLagPanelProps { pairs: LagPair[]; laggingCount: number; thresholdMs: number; }
export function DepLagPanel({ pairs, laggingCount, thresholdMs }: DepLagPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐌 Dependency Lag</h3>
        <span className={`text-xs ${laggingCount > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {laggingCount > 0 ? `⚠ ${laggingCount} lagging` : "✅ All fast"} ({">"}{thresholdMs}ms)
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pairs.map(p => (
          <div key={`${p.source}→${p.destination}`} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.source} → {p.destination}</span>
            <span className="text-yellow-600">avg {p.avgMs}ms · max {p.maxMs}ms · {p.calls} calls</span>
          </div>
        ))}
      </div>
    </div>
  );
}
