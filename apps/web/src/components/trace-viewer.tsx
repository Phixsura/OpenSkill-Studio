"use client";

interface SpanData { spanId: string; name: string; parentSpanId: string; status: string; durationMs: number; }

const statusColors: Record<string, string> = { ok: "bg-green-500", error: "bg-red-500", unset: "bg-gray-400" };

export function TraceViewer({ spans, traceId }: { spans: SpanData[]; traceId: string }) {
  const maxDuration = Math.max(...spans.map(s => s.durationMs), 1);
  const root = spans.find(s => !s.parentSpanId);
  const children = (parentId: string) => spans.filter(s => s.parentSpanId === parentId);

  const renderSpan = (span: SpanData, depth: number = 0): JSX.Element => (
    <div key={span.spanId}>
      <div className="flex items-center gap-2 py-1" style={{ paddingLeft: `${depth * 20}px` }}>
        <span className={`w-2 h-2 rounded-full ${statusColors[span.status] || "bg-gray-400"}`} />
        <span className="text-xs font-medium flex-1">{span.name}</span>
        <div className="w-32 h-2 bg-gray-100 dark:bg-gray-800 rounded-full">
          <div className={`h-full rounded-full ${statusColors[span.status] || "bg-blue-500"}`}
            style={{ width: `${(span.durationMs / maxDuration) * 100}%` }} />
        </div>
        <span className="text-[10px] text-gray-400 w-14 text-right">{span.durationMs}ms</span>
      </div>
      {children(span.spanId).map(c => renderSpan(c, depth + 1))}
    </div>
  );

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-500">
        <span className="font-mono">Trace: {traceId.slice(0, 16)}...</span>
        <span>{spans.length} spans</span>
      </div>
      <div className="border dark:border-gray-700 rounded-xl p-3">
        {root ? renderSpan(root) : <span className="text-xs text-gray-400">No spans</span>}
      </div>
    </div>
  );
}
