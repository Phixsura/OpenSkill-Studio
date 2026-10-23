"use client";

interface Span { spanId: string; parentSpanId: string | null; operation: string; service: string; startedAt: string; }
interface TraceWaterfallProps { spans: Span[]; totalSpans: number; services: string[]; maxDepth: number; }

const svcColors = ["bg-blue-500", "bg-green-500", "bg-purple-500", "bg-orange-500", "bg-pink-500"];

export function TraceWaterfall({ spans, totalSpans, services, maxDepth }: TraceWaterfallProps) {
  const colorMap = Object.fromEntries(services.map((s, i) => [s, svcColors[i % svcColors.length]]));
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Trace</h3>
        <span className="text-xs text-gray-400">{totalSpans} spans · {services.length} services · depth {maxDepth}</span>
      </div>
      <div className="space-y-1">
        {spans.map(s => {
          const depth = s.parentSpanId ? 1 : 0; // simplified
          return (
            <div key={s.spanId} className="flex items-center gap-2" style={{ paddingLeft: depth * 24 }}>
              <div className={`h-4 rounded ${colorMap[s.service] ?? "bg-gray-400"}`} style={{ width: 80 }} />
              <span className="text-xs font-mono">{s.operation}</span>
              <span className="text-xs text-gray-400">{s.service}</span>
            </div>
          );
        })}
      </div>
      <div className="flex gap-3">
        {services.map(s => (
          <div key={s} className="flex items-center gap-1 text-xs">
            <span className={`h-2 w-2 rounded ${colorMap[s]}`} />
            <span>{s}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
