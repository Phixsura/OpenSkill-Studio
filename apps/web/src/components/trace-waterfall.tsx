"use client";

interface Span { spanId: string; operation: string; durationMs: number; parentId: string | null; }
interface TraceWaterfallProps { traceId: string; spans: Span[]; totalDurationMs: number;
  criticalSpan: string | null; depth: number; }

export function TraceWaterfall({ traceId, spans, totalDurationMs, criticalSpan, depth }: TraceWaterfallProps) {
  const maxDur = Math.max(...spans.map(s => s.durationMs), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Trace Waterfall</h3>
        <div className="text-xs text-gray-400">
          {spans.length} spans · {totalDurationMs}ms · depth {depth}
        </div>
      </div>
      <div className="p-2 text-[10px] text-gray-400 font-mono border-b dark:border-gray-700 px-4">
        trace: {traceId} {criticalSpan && `· bottleneck: ${criticalSpan}`}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {spans.map(s => {
          const pct = Math.round((s.durationMs / maxDur) * 100);
          const isCritical = s.operation === criticalSpan;
          return (
            <div key={s.spanId} className="px-4 py-1.5">
              <div className="flex items-center justify-between text-xs mb-0.5">
                <span className={`font-mono ${isCritical ? "text-red-600 font-bold" : ""}`}>
                  {s.parentId ? "└─ " : ""}{s.operation}
                </span>
                <span className="text-gray-400">{s.durationMs}ms</span>
              </div>
              <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
                <div className={`h-full rounded-full ${isCritical ? "bg-red-500" : "bg-blue-400"}`}
                  style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
