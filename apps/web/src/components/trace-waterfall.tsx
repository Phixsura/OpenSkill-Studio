"use client";

interface Span { span_id: string; service: string; operation: string; duration_ms: number; status: string; }
interface TraceWaterfallProps { traceId: string; spans: Span[]; totalDurationMs: number; }

export function TraceWaterfall({ traceId, spans, totalDurationMs }: TraceWaterfallProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Trace</h3>
        <span className="font-mono text-xs text-gray-400">{traceId}</span>
      </div>
      <p className="text-xs text-gray-400">{spans.length} spans · {totalDurationMs}ms total</p>
      <div className="mt-3 space-y-1">
        {spans.map(s => {
          const widthPct = Math.max(5, Math.round((s.duration_ms / Math.max(totalDurationMs, 1)) * 100));
          return (
            <div key={s.span_id} className="flex items-center gap-2">
              <span className="w-20 truncate text-xs">{s.service}</span>
              <div className="flex-1">
                <div className={`h-4 rounded text-xs leading-4 px-1 text-white ${s.status === "error" ? "bg-red-500" : "bg-blue-500"}`}
                  style={{ width: `${widthPct}%` }}>
                  {s.duration_ms}ms
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
