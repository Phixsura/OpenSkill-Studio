"use client";

interface Props { ackRate: number; avgLatencyMs: number; unackedCount: number; totalDeliveries: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgmentCard({ ackRate, avgLatencyMs, unackedCount, totalDeliveries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Webhook Acks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unackedCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">{unackedCount} unacked</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className={`font-semibold ${ackRate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{ackRate}%</div><div className="text-gray-400">Ack Rate</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{avgLatencyMs}ms</div><div className="text-gray-400">Avg Latency</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalDeliveries.toLocaleString()}</div><div className="text-gray-400">Delivered</div></div>
      </div>
    </div>
  );
}
