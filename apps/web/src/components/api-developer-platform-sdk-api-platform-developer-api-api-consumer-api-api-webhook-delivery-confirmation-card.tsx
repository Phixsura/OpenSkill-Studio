"use client";

interface Props { confirmationRate: number; pendingCount: number; confirmedCount: number; timeoutCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmationCard({ confirmationRate, pendingCount, confirmedCount, timeoutCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Delivery Confirmation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${confirmationRate >= 90 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{confirmationRate}%</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-yellow-600">{pendingCount}</div><div className="text-gray-400">Pending</div></div>
        <div><div className="font-semibold text-green-600">{confirmedCount}</div><div className="text-gray-400">Confirmed</div></div>
        <div><div className="font-semibold text-red-600">{timeoutCount}</div><div className="text-gray-400">Timeout</div></div>
      </div>
    </div>
  );
}
