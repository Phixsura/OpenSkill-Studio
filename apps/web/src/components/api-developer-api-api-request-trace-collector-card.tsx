"use client";

interface SpanInfo { span_id: string; operation: string; service: string; duration_ms: number; status: string; }
interface TraceInfo { trace_id: string; spans: SpanInfo[]; total_duration_ms: number; has_errors: boolean; }
interface Props { traces: TraceInfo[]; errorCount: number; traceCount: number; appName: string; }

export default function APIDeveloperAPIApiRequestTraceCollectorCard({ traces, errorCount, traceCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔎 Request Traces</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {traceCount} traces</p>
        </div>
        {errorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{errorCount} errors</span>}
      </div>
      {traces.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traces</p>
      ) : (
        <div className="space-y-2">
          {traces.map((t) => (
            <div key={t.trace_id} className={`rounded-lg p-2 ${t.has_errors ? "bg-red-50 dark:bg-red-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-mono text-gray-700 dark:text-gray-300">{t.trace_id}</span>
                <span className="text-gray-400">{t.spans.length} spans · {t.total_duration_ms}ms</span>
              </div>
              <div className="mt-0.5 flex gap-1">
                {t.spans.slice(0, 4).map((s) => (
                  <span key={s.span_id} className={`rounded px-1 py-0.5 text-[9px] ${s.status === "error" ? "bg-red-100 text-red-700" : "bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200"}`}>{s.service}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
