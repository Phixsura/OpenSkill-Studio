"use client";

interface HealthInfo { consumer_id: string; success_rate: number; health_grade: string; total_deliveries: number; avg_latency_ms: number; }
interface Props { reports: HealthInfo[]; unhealthyCount: number; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export default function APIDeveloperPlatformSDKApiConsumerWebhookHealthReportCard({ reports, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Consumer Webhook Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health data</p>
      ) : (
        <div className="space-y-1">
          {reports.slice(0, 5).map((r) => (
            <div key={r.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`text-sm font-black ${gColor[r.health_grade] ?? ""}`}>{r.health_grade}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.consumer_id}</span>
              </div>
              <span className="text-gray-400">{r.success_rate}% · {r.total_deliveries.toLocaleString()} del</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
