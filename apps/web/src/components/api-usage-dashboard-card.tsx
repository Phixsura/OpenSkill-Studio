"use client";

interface DashInfo { total_requests: number; total_errors: number; error_rate: number; unique_consumers: number; unique_endpoints: number; avg_latency_ms: number; peak_rpm: number; quota_usage_pct: number; }
interface Props { dashboard: DashInfo; appName: string; }

export default function APIUsageDashboardCard({ dashboard: d, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Dashboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { l: "Requests", v: d.total_requests.toLocaleString() },
          { l: "Error Rate", v: `${d.error_rate}%` },
          { l: "Consumers", v: d.unique_consumers },
          { l: "Endpoints", v: d.unique_endpoints },
          { l: "Avg Latency", v: `${d.avg_latency_ms}ms` },
          { l: "Peak RPM", v: d.peak_rpm },
          { l: "Quota", v: `${d.quota_usage_pct}%` },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
