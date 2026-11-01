"use client";

interface AnalyticsInfo { total_impressions: number; total_clicks: number; unique_viewers: number; entries_read: number; ctr: number; read_rate: number; }
interface Props { analytics: AnalyticsInfo; appName: string; }

export default function APIDeveloperAPIChangelogWidgetAnalyticsCard({ analytics: a, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Widget Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{a.total_impressions.toLocaleString()}</p>
          <p className="text-[8px] text-gray-500">Impressions</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-blue-600">{a.ctr}%</p>
          <p className="text-[8px] text-gray-500">CTR</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">{a.read_rate}%</p>
          <p className="text-[8px] text-gray-500">Read Rate</p>
        </div>
      </div>
    </div>
  );
}
