"use client";

interface RetryInfo { webhookId: string; attempt: number; delayMs: number; url: string; }
interface WhRetryPanelProps { pending: RetryInfo[]; succeeded: number; failed: number; }

export function WhRetryPanel({ pending, succeeded, failed }: WhRetryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Webhook Retries</h3>
        <span className="text-xs text-gray-400">{pending.length} pending · {succeeded} ok · {failed} failed</span>
      </div>
      {pending.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {pending.map(r => (
            <div key={`${r.webhookId}-${r.attempt}`} className="flex items-center justify-between px-4 py-1.5 text-xs">
              <span className="font-mono truncate max-w-[200px]">{r.url}</span>
              <span className="text-gray-400">#{r.attempt} · {r.delayMs}ms</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No pending retries</div>
      )}
    </div>
  );
}
