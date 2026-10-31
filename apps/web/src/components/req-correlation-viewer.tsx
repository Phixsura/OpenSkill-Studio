"use client";

interface Trace { correlationId: string; spanCount: number; totalMs: number; services: string[]; }
interface ReqCorrelationViewerProps { traces: Trace[]; totalTraces: number; totalSpans: number; }

export function ReqCorrelationViewer({ traces, totalTraces, totalSpans }: ReqCorrelationViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Request Correlation</h3>
        <span className="text-xs text-gray-400">{totalTraces} traces · {totalSpans} spans</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {traces.map(t => (
          <div key={t.correlationId} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-blue-500">{t.correlationId}</span>
              <span className="text-xs text-gray-400">{t.spanCount} spans · {t.totalMs}ms</span>
            </div>
            <div className="flex gap-1 mt-0.5">
              {t.services.map(s => (
                <span key={s} className="px-1 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded">{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
