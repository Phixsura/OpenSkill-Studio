"use client";
interface WaterfallSpan { service: string; operation: string; durationMs: number; offsetPct: number; widthPct: number; depth: number; }
interface TraceWaterfallPanelProps { spans: WaterfallSpan[]; totalMs: number; spanCount: number; }
const DEPTH_COLOR = ["bg-blue-500", "bg-green-500", "bg-yellow-500", "bg-purple-500", "bg-red-500"];
export function TraceWaterfallPanel({ spans, totalMs, spanCount }: TraceWaterfallPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌊 Trace Waterfall</h3>
        <span className="text-xs text-gray-400">{spanCount} spans · {totalMs}ms</span>
      </div>
      <div className="p-4 space-y-1">
        {spans.map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-[10px]" style={{ paddingLeft: `${s.depth * 16}px` }}>
            <span className="w-16 text-gray-500 truncate">{s.service}</span>
            <div className="flex-1 h-4 bg-gray-100 dark:bg-gray-800 rounded relative">
              <div className={`absolute h-full rounded ${DEPTH_COLOR[s.depth % 5]}`}
                style={{ left: `${s.offsetPct}%`, width: `${Math.max(s.widthPct, 1)}%` }} />
            </div>
            <span className="w-12 text-right text-gray-400">{s.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
