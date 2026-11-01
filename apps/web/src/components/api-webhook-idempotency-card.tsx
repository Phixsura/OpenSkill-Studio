"use client";

interface IdempotencyInfo { total_keys: number; duplicates_prevented: number; delivered: number; }
interface Props { stats: IdempotencyInfo; appName: string; }

export default function APIWebhookIdempotencyCard({ stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Webhook Idempotency</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{stats.total_keys}</p>
          <p className="text-[8px] text-gray-500">Keys</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">{stats.delivered}</p>
          <p className="text-[8px] text-gray-500">Delivered</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-yellow-600">{stats.duplicates_prevented}</p>
          <p className="text-[8px] text-gray-500">Deduped</p>
        </div>
      </div>
    </div>
  );
}
