"use client";

interface TraceAnalyzerProps { spanCount: number; totalMs: number; bottleneck: string | null;
  bottleneckMs: number; services: string[]; errorSpans: number; hasErrors: boolean; }

export function TraceAnalyzer({ spanCount, totalMs, bottleneck, bottleneckMs, services, errorSpans, hasErrors }: TraceAnalyzerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Trace Analysis</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{spanCount} spans · {totalMs}ms</span>
          {hasErrors && <span className="text-red-500">{errorSpans} errors</span>}
        </div>
      </div>
      <div className="p-3 text-xs">
        {bottleneck && <div className="text-yellow-600 mb-1">⚠ Bottleneck: {bottleneck} ({bottleneckMs}ms)</div>}
        <div className="text-gray-400">Services: {services.join(", ")}</div>
      </div>
    </div>
  );
}
