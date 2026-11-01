"use client";

interface ReportInfo { report_id: string; period: string; total_deliveries: number; success_rate: number; health_status: string; avg_latency_ms: number; destinations_count: number; }
interface Props { reports: ReportInfo[]; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReportCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Delivery Reports</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {reports.length} periods</p>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery reports</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.report_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.period}</span>
                <span className={`font-bold ${hColor[r.health_status] ?? ""}`}>{r.success_rate}% {r.health_status}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>{r.total_deliveries.toLocaleString()} total</span>
                <span>{r.avg_latency_ms}ms avg</span>
                <span>{r.destinations_count} destinations</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
