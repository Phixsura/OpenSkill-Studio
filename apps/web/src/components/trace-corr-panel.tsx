"use client";

interface TraceInfo { traceId: string; spans: number; services: string[]; durationMs: number; }
interface TraceCorrPanelProps { traces: TraceInfo[]; totalTraces: number; totalSpans: number; }

export function TraceCorrPanel({ traces, totalTraces, totalSpans }: TraceCorrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Trace Correlator</h3>
        <span className="text-xs text-gray-400">{totalTraces} traces · {totalSpans} spans</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {traces.map(t => (
          <div key={t.traceId} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono">{t.traceId}</span>
              <span className={`font-bold ${t.durationMs > 1000 ? "text-red-500" : "text-gray-400"}`}>{t.durationMs}ms</span>
            </div>
            <div className="text-gray-400">{t.spans} spans · {t.services.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
