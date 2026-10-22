"use client";

interface TimelineEvent { event: string; timestamp: string | null; }
interface DeliveryInspectorProps { eventType: string; url: string; status: string; httpStatus: number | null;
  durationMs: number | null; attempt: number; maxAttempts: number; error: string | null; timeline: TimelineEvent[]; }

export function DeliveryInspector({ eventType, url, status, httpStatus, durationMs, attempt, maxAttempts, error, timeline }: DeliveryInspectorProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <span className="font-mono text-sm font-semibold">{eventType}</span>
        <span className={`rounded px-2 py-0.5 text-xs ${status === "delivered" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>{status}</span>
      </div>
      <div className="mb-3 space-y-1 text-sm text-gray-600">
        <p>URL: <code className="text-xs">{url}</code></p>
        {httpStatus && <p>HTTP: {httpStatus}</p>}
        {durationMs != null && <p>Duration: {durationMs}ms</p>}
        <p>Attempt: {attempt}/{maxAttempts}</p>
        {error && <p className="text-red-600">Error: {error}</p>}
      </div>
      <div className="space-y-1">
        {timeline.map((t, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="font-medium">{t.event}</span>
            <span className="text-gray-400">{t.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
