"use client";

interface ReceiptInfo { delivery_id: string; destination: string; status_code: number; acknowledged: boolean; response_time_ms: number; retry_number: number; }
interface Props { receipts: ReceiptInfo[]; ackRate: number; avgResponseTime: number; unacknowledgedCount: number; appName: string; }

export default function APIDeveloperAPIApiWebhookDeliveryReceiptCard({ receipts, ackRate, avgResponseTime, unacknowledgedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✉️ Delivery Receipts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-sm font-bold ${ackRate >= 95 ? "text-green-600" : "text-red-500"}`}>{ackRate}%</span>
          <p className="text-[9px] text-gray-400">avg {avgResponseTime}ms</p>
        </div>
      </div>
      {unacknowledgedCount > 0 && <p className="mb-2 text-[10px] text-red-500">{unacknowledgedCount} unacknowledged</p>}
      {receipts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No receipts</p>
      ) : (
        <div className="space-y-1">
          {receipts.map((r) => (
            <div key={r.delivery_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${r.acknowledged ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{r.delivery_id}</span>
              </div>
              <span className="text-gray-400">{r.status_code} · {r.response_time_ms}ms{r.retry_number > 0 ? ` · retry #${r.retry_number}` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
