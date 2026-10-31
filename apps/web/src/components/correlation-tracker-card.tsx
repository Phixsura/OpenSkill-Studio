"use client";

interface SpanInfo {
  span_id: string;
  service: string;
  operation: string;
  status: "ok" | "error";
  duration_ms: number | null;
  parent_span_id: string | null;
  depth: number;
}

interface CorrelationTrackerCardProps {
  traceId: string;
  spans: SpanInfo[];
  appName: string;
}

export default function CorrelationTrackerCard({
  traceId,
  spans,
  appName,
}: CorrelationTrackerCardProps) {
  const errorCount = spans.filter((s) => s.status === "error").length;
  const totalMs = spans.reduce((max, s) => Math.max(max, s.duration_ms ?? 0), 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Trace</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] text-gray-400">{traceId}</span>
          {errorCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {errorCount} errors
            </span>
          )}
        </div>
      </div>

      {spans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No spans</p>
      ) : (
        <div className="space-y-1">
          {spans.map((s) => (
            <div
              key={s.span_id}
              className="flex items-center gap-2"
              style={{ paddingLeft: `${s.depth * 16}px` }}
            >
              <span
                className={`h-2 w-2 rounded-full ${s.status === "error" ? "bg-red-500" : "bg-green-500"}`}
              />
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                {s.service}
              </span>
              <span className="text-[11px] text-gray-400">{s.operation}</span>
              {s.duration_ms !== null && (
                <span className="ml-auto font-mono text-[11px] text-gray-400">
                  {s.duration_ms.toFixed(1)}ms
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {totalMs > 0 && (
        <p className="mt-3 text-center text-[11px] text-gray-400">
          {spans.length} spans · {totalMs.toFixed(0)}ms total
        </p>
      )}
    </div>
  );
}
