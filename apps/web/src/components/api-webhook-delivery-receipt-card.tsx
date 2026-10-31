"use client";

interface ReceiptInfo { receipt_id: string; destination: string; status_code: number; response_time_ms: number; acknowledged: boolean; }
interface Props { receipts: ReceiptInfo[]; acknowledgedRate: number; totalCount: number; appName: string; }

export default function APIWebhookDeliveryReceiptCard({ receipts, acknowledgedRate, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✉️ Delivery Receipts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{totalCount} deliveries</span>
          <p className={`text-[10px] font-medium ${acknowledgedRate >= 95 ? "text-green-600" : "text-red-500"}`}>{acknowledgedRate}% acknowledged</p>
        </div>
      </div>
      {receipts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No receipts</p>
      ) : (
        <div className="space-y-1">
          {receipts.map((r) => (
            <div key={r.receipt_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${r.acknowledged ? "bg-green-500" : "bg-red-500"}`} />
                <span className="truncate max-w-[150px] text-gray-700 dark:text-gray-300">{r.destination}</span>
              </div>
              <span className="text-gray-400">{r.status_code} · {r.response_time_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
