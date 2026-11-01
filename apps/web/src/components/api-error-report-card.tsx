"use client";

interface ErrorItem { error_code: string; count: number; }
interface ReportInfo { report_id: string; period: string; errors: ErrorItem[]; total_errors: number; error_rate: number; }
interface APIErrorReportCardProps { reports: ReportInfo[]; appName: string; }

export default function APIErrorReportCard({ reports, appName }: APIErrorReportCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📉 Error Reports</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{reports.length} reports</span>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error reports</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.report_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.period}</span>
                <span className={`text-[11px] font-medium ${r.error_rate > 1 ? "text-red-500" : "text-green-600"}`}>{r.error_rate}% error rate</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{r.total_errors} errors · {r.errors.length} types</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
