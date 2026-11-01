"use client";

interface TraceInfo { trace_id: string; span_count: number; total_duration_ms: number; has_errors: boolean; }
interface Props { traces: TraceInfo[]; failedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelationCard({ traces, failedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Request Traces</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {traces.length} traces</p>
        </div>
        {failedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">❌ {failedCount} failed</span>}
      </div>
      {traces.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traces</p>
      ) : (
        <div className="space-y-1">
          {traces.map((t) => (
            <div key={t.trace_id} className="flex items-center justify-between text-[11px]">
              <span className={`font-mono ${t.has_errors ? "text-red-600 dark:text-red-400" : "text-gray-700 dark:text-gray-300"}`}>{t.trace_id.slice(0, 12)}...</span>
              <span className="text-gray-400">{t.span_count} spans · {Math.round(t.total_duration_ms)}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
