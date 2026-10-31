"use client";

interface Period { period: string; deliveries: number; successRate: number; avgMs: number; }
interface Props { webhookId: string; totalDeliveries: number; overallRate: number; avgMs: number; trend: string; periods: Period[]; appName: string; }

const trendIcons: Record<string, string> = { improving: "📈", stable: "➡️", declining: "📉" };

export default function APIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalyticsCard({ webhookId, totalDeliveries, overallRate, avgMs, trend, periods, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Delivery Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {webhookId}</p>
        </div>
        <span className={`text-lg font-bold ${overallRate >= 95 ? "text-green-600" : overallRate >= 80 ? "text-amber-600" : "text-red-600"}`}>{overallRate}%</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[10px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalDeliveries.toLocaleString()}</div><div className="text-gray-400">Deliveries</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{avgMs}ms</div><div className="text-gray-400">Avg Latency</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{trendIcons[trend]} {trend}</div><div className="text-gray-400">Trend</div></div>
      </div>
      {periods.length > 0 && (
        <div className="space-y-0.5">
          {periods.slice(-5).map((p) => (
            <div key={p.period} className="flex justify-between text-[9px] text-gray-500">
              <span>{p.period}</span>
              <span>{p.deliveries} del · {p.successRate}% · {p.avgMs}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
