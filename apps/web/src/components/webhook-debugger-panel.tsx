"use client";

interface DeliveryAttempt { event_type: string; status_code: number; success: boolean; response_time_ms: number; timestamp: string; }
interface WebhookDebuggerPanelProps { attempts: DeliveryAttempt[]; onReplay: (index: number) => void; }

export function WebhookDebuggerPanel({ attempts, onReplay }: WebhookDebuggerPanelProps) {
  if (attempts.length === 0) return <p className="text-sm text-gray-400">No delivery attempts.</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700"><h3 className="text-sm font-semibold">Webhook Debugger</h3></div>
      <div className="max-h-64 overflow-y-auto">
        {attempts.map((a, i) => (
          <div key={i} className={`flex items-center gap-3 border-b px-3 py-2 text-xs dark:border-gray-700 ${a.success ? "" : "bg-red-50 dark:bg-red-900/10"}`}>
            <span>{a.success ? "✅" : "❌"}</span>
            <span className="flex-1">{a.event_type}</span>
            <span className={a.success ? "text-green-600" : "text-red-600"}>{a.status_code}</span>
            <span className="text-gray-400">{a.response_time_ms}ms</span>
            {!a.success && <button onClick={() => onReplay(i)} className="rounded bg-blue-100 px-1.5 py-0.5 text-blue-700">↻</button>}
          </div>
        ))}
      </div>
    </div>
  );
}
