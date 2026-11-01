"use client";

interface Props { confirmationRate: number; avgLatencyMs: number; unconfirmedCount: number; totalDeliveries: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmationCard({ confirmationRate, avgLatencyMs, unconfirmedCount, totalDeliveries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Delivery Confirmation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unconfirmedCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{unconfirmedCount} pending</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${confirmationRate >= 95 ? "text-green-600" : "text-red-500"}`}>{confirmationRate}%</p>
          <p className="text-[9px] text-gray-400">Confirmed</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{avgLatencyMs}ms</p>
          <p className="text-[9px] text-gray-400">Avg Latency</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{totalDeliveries}</p>
          <p className="text-[9px] text-gray-400">Total</p>
        </div>
      </div>
    </div>
  );
}
