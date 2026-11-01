"use client";

interface ReportInfo { report_id: string; period: string; uptime_pct: number; downtime_minutes: number; incidents: number; }
interface Props { reports: ReportInfo[]; appName: string; }

export default function APIDeveloperAPIUptimeReportCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📶 Uptime Reports</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{reports.length} reports</span>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No uptime reports</p>
      ) : (
        <div className="space-y-1.5">
          {reports.map((r) => (
            <div key={r.report_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.period}</span>
              <span className="text-gray-400">
                <span className={r.uptime_pct >= 99.9 ? "text-green-600 font-medium" : "text-yellow-600"}>{r.uptime_pct}%</span>
                {" · "}{r.downtime_minutes}min down · {r.incidents} incidents
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
