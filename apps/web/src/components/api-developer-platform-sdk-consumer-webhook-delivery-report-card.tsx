"use client";

interface Period { period: string; total: number; successful: number; failed: number; avgMs: number; successRate: number; }
interface Props { webhookId: string; periods: Period[]; overallSuccessRate: number; trend: string; consumerId: string; appName: string; }

const trendIcons: Record<string, string> = { improving: "📈", declining: "📉", stable: "➡️" };

export default function APIDeveloperPlatformSDKConsumerWebhookDeliveryReportCard({ webhookId, periods, overallSuccessRate, trend, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Delivery Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {webhookId}</p>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${overallSuccessRate >= 95 ? "text-green-600" : overallSuccessRate >= 80 ? "text-amber-600" : "text-red-600"}`}>{overallSuccessRate}%</div>
          <div className="text-[10px] text-gray-400">{trendIcons[trend]} {trend}</div>
        </div>
      </div>
      {periods.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery data</p>
      ) : (
        <div className="space-y-1">
          {periods.slice(-7).map((p) => (
            <div key={p.period} className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500">{p.period}</span>
              <div className="flex gap-2">
                <span className="text-green-500">{p.successful}✓</span>
                {p.failed > 0 && <span className="text-red-500">{p.failed}✗</span>}
                <span className="text-gray-400">{p.avgMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
