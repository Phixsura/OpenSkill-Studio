"use client";

interface RetryEntry { webhookId: string; url: string; attempts: number;
  maxRetries: number; status: string; }
interface WebhookRetryQueueProps { entries: RetryEntry[]; deliveryRate: number;
  retrying: number; failed: number; }

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-200 text-gray-600", retrying: "bg-yellow-100 text-yellow-700",
  delivered: "bg-green-100 text-green-700", failed: "bg-red-100 text-red-700",
};

export function WebhookRetryQueue({ entries, deliveryRate, retrying, failed }: WebhookRetryQueueProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔁 Webhook Retries</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{deliveryRate}% delivered</span>
          {retrying > 0 && <span className="text-yellow-600">{retrying} retrying</span>}
          {failed > 0 && <span className="text-red-500">{failed} failed</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.webhookId} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-mono">{e.webhookId}</span>
              <span className="text-gray-400 ml-2 truncate max-w-[150px] inline-block align-bottom">{e.url}</span>
            </div>
            <div className="flex gap-2">
              <span className="text-gray-400">{e.attempts}/{e.maxRetries}</span>
              <span className={`px-1.5 py-0.5 rounded ${STATUS_COLORS[e.status] ?? ""}`}>{e.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
