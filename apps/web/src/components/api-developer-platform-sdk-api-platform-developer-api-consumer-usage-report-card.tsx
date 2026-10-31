"use client";

interface Metrics { total_requests: number; success_rate: number; avg_latency_ms: number; data_transferred_bytes: number; }
interface Props { consumerId: string; metrics: Metrics; period: string; appName: string; }

const fmtBytes = (b: number) => b >= 1048576 ? `${(b / 1048576).toFixed(1)} MB` : b >= 1024 ? `${(b / 1024).toFixed(0)} KB` : `${b} B`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReportCard({ consumerId, metrics, period, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Usage Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} ({period})</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{metrics.total_requests.toLocaleString()}</div><div className="text-gray-400">Requests</div></div>
        <div><div className={`font-semibold ${metrics.success_rate >= 99 ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"}`}>{metrics.success_rate}%</div><div className="text-gray-400">Success</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{metrics.avg_latency_ms}ms</div><div className="text-gray-400">Avg Latency</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{fmtBytes(metrics.data_transferred_bytes)}</div><div className="text-gray-400">Data</div></div>
      </div>
    </div>
  );
}
