"use client";

interface ReportInfo {
  report_id: string;
  name: string;
  schedule: string;
  format: string;
  recipients: string[];
  enabled: boolean;
  generation_count: number;
}

interface ScheduledReportCardProps {
  reports: ReportInfo[];
  appName: string;
}

const FORMAT_ICONS: Record<string, string> = { pdf: "📄", csv: "📊", html: "🌐" };
const SCHEDULE_COLORS: Record<string, string> = {
  daily: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  weekly: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  monthly: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function ScheduledReportCard({ reports, appName }: ScheduledReportCardProps) {
  const enabledCount = reports.filter((r) => r.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Scheduled Reports
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{enabledCount} active</span>
      </div>

      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scheduled reports</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div
              key={r.report_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!r.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{FORMAT_ICONS[r.format] ?? "📋"}</span>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{r.name}</span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${SCHEDULE_COLORS[r.schedule] ?? "bg-gray-100 text-gray-600"}`}
                  >
                    {r.schedule}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">{r.generation_count} sent</span>
              </div>
              <p className="mt-0.5 text-[11px] text-gray-400">{r.recipients.join(", ")}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
