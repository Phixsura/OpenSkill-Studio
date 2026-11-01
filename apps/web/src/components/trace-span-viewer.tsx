"use client";

interface SpanInfo { spanId: string; service: string; operation: string; durationMs: number; depth: number; }
interface TraceSpanViewerProps { spans: SpanInfo[]; totalMs: number; services: number; }

export function TraceSpanViewer({ spans, totalMs, services }: TraceSpanViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Trace Spans</h3>
        <span className="text-xs text-gray-400">{spans.length} spans · {services} services · {totalMs}ms</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {spans.map(s => (
          <div key={s.spanId} className="px-4 py-1.5 text-xs" style={{ paddingLeft: `${16 + s.depth * 16}px` }}>
            <div className="flex items-center justify-between">
              <div>
                <span className="text-blue-500 font-semibold">{s.service}</span>
                <span className="text-gray-400 ml-1">{s.operation}</span>
              </div>
              <span className="font-mono text-gray-400">{s.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
