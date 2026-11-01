"use client";
interface ReportInfo { report_id: string; period: string; total_events: number; total_deliveries: number; success_rate: number; avg_latency_ms: number; top_event: string; }
interface Props { reports: ReportInfo[]; appName: string; }
export default function APIDeveloperAPIWebhookSummaryReportCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div><h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Webhook Reports</h3><p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p></div>
        <span className="text-xs text-gray-400">{reports.length} reports</span>
      </div>
      {reports.length === 0 ? (<p className="text-center text-sm text-gray-400">No reports</p>) : (
        <div className="space-y-1.5">{reports.map((r) => (
          <div key={r.report_id} className="flex items-center justify-between text-[11px]">
            <span className="text-gray-700 dark:text-gray-300">{r.period}</span>
            <span className="text-gray-400">{r.total_deliveries.toLocaleString()} delivered · {r.success_rate}% · {r.avg_latency_ms}ms</span>
          </div>
        ))}</div>
      )}
    </div>
  );
}
