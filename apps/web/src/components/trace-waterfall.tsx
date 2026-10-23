"use client";

interface Span { spanId: string; parent: string | null; service: string;
  operation: string; durationMs: number; status: string; }
interface TraceWaterfallProps { traceId: string; spans: Span[]; totalDurationMs: number;
  serviceCount: number; errorCount: number; }

const STATUS_COLOR: Record<string, string> = { ok: "bg-blue-500", error: "bg-red-500", active: "bg-yellow-500" };

export function TraceWaterfall({ traceId, spans, totalDurationMs, serviceCount, errorCount }: TraceWaterfallProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">🔗 Trace Waterfall</h3>
          <span className="text-xs text-gray-400">{totalDurationMs}ms</span>
        </div>
        <div className="flex gap-3 mt-1 text-xs text-gray-400">
          <span>Trace: <code>{traceId.slice(0, 12)}…</code></span>
          <span>{spans.length} spans</span>
          <span>{serviceCount} services</span>
          {errorCount > 0 && <span className="text-red-500">{errorCount} errors</span>}
        </div>
      </div>
      <div className="p-4 space-y-1.5">
        {spans.map((s, i) => (
          <div key={s.spanId} className="flex items-center gap-2" style={{ paddingLeft: s.parent ? 24 : 0 }}>
            <span className="text-xs text-gray-400 w-16 shrink-0">{s.service}</span>
            <div className="flex-1 h-5 bg-gray-100 dark:bg-gray-800 rounded relative">
              <div className={`h-full rounded ${STATUS_COLOR[s.status] || "bg-gray-400"}`}
                   style={{ width: `${Math.max((s.durationMs / Math.max(totalDurationMs, 1)) * 100, 5)}%` }} />
              <span className="absolute inset-0 flex items-center px-2 text-[10px] text-white font-medium truncate">
                {s.operation} · {s.durationMs}ms
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
