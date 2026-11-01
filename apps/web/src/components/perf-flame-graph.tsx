"use client";

interface SpanProfile { name: string; selfMs: number; durationMs: number; pct: number; }
interface PerfFlameGraphProps { spans: SpanProfile[]; totalMs: number;
  bottleneck: string | null; improvementPct?: number; }

export function PerfFlameGraph({ spans, totalMs, bottleneck, improvementPct }: PerfFlameGraphProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Performance Profile</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalMs}ms total</span>
          {bottleneck && <span className="text-red-500">bottleneck: {bottleneck}</span>}
          {improvementPct !== undefined && (
            <span className={improvementPct > 0 ? "text-green-600" : "text-red-500"}>
              {improvementPct > 0 ? "↑" : "↓"}{Math.abs(improvementPct)}% faster
            </span>
          )}
        </div>
      </div>
      <div className="p-4 space-y-1">
        {spans.map(s => (
          <div key={s.name} className="flex items-center gap-2">
            <span className="text-xs font-mono w-24 truncate">{s.name}</span>
            <div className="flex-1 h-5 bg-gray-100 dark:bg-gray-800 rounded relative">
              <div className={`h-full rounded ${s.name === bottleneck ? "bg-red-500" : "bg-orange-400"}`}
                style={{ width: `${Math.max(s.pct, 2)}%` }}>
                <span className="text-[10px] text-white px-1 leading-5">{s.selfMs}ms ({s.pct}%)</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
