"use client";

interface Span { span_id: string; service: string; operation: string; duration_ms: number; children: Span[]; }
interface TraceWaterfallViewProps { roots: Span[]; totalSpans: number; totalDurationMs: number; services: string[]; }

function SpanRow({ span, totalMs, depth }: { span: Span; totalMs: number; depth: number }) {
  const pct = Math.max((span.duration_ms / Math.max(totalMs, 1)) * 100, 2);
  return (
    <>
      <div className="flex items-center gap-1 py-1" style={{ paddingLeft: `${depth * 16}px` }}>
        <span className="w-20 truncate text-xs text-blue-500">{span.service}</span>
        <span className="flex-1 text-xs">{span.operation}</span>
        <div className="w-32">
          <div className="h-3 rounded bg-blue-400" style={{ width: `${pct}%`, opacity: 0.6 + depth * 0.1 }} />
        </div>
        <span className="w-14 text-right text-xs text-gray-400">{span.duration_ms}ms</span>
      </div>
      {span.children.map(c => <SpanRow key={c.span_id} span={c} totalMs={totalMs} depth={depth + 1} />)}
    </>
  );
}

export function TraceWaterfallView({ roots, totalSpans, totalDurationMs, services }: TraceWaterfallViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Trace Waterfall</h2>
        <span className="text-xs text-gray-400">{totalSpans} spans · {totalDurationMs}ms · {services.length} services</span>
      </div>
      <div className="rounded border p-2 dark:border-gray-700">
        {roots.map(r => <SpanRow key={r.span_id} span={r} totalMs={totalDurationMs} depth={0} />)}
      </div>
    </div>
  );
}
