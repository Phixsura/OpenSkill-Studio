"use client";
interface SignalAggPanelProps { compositeScore: number; status: string;
  signals: Record<string, number>; sources: number; }
const STATUS_STYLE: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function SignalAggPanel({ compositeScore, status, signals, sources }: SignalAggPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${STATUS_STYLE[status] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{compositeScore}</div>
        <div className="text-xs">{status.toUpperCase()} · {sources} sources</div>
      </div>
      <div className="p-4 space-y-1.5">
        {Object.entries(signals).map(([src, pct]) => (
          <div key={src}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="text-gray-500 capitalize">{src}</span>
              <span className="text-gray-400">{pct}%</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${pct >= 90 ? "bg-green-500" : pct >= 70 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
