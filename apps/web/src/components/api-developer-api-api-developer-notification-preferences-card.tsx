"use client";

interface PrefInfo { developer_id: string; enabled_channels: string[]; enabled_categories: string[]; quiet_hours_start: number | null; quiet_hours_end: number | null; }
interface Props { preference: PrefInfo; appName: string; }

export default function APIDeveloperAPIApiDeveloperNotificationPreferencesCard({ preference: p, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Notification Preferences</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {p.developer_id}</p>
      </div>
      <div className="mb-3">
        <p className="text-[10px] font-medium text-gray-500 mb-1">Channels</p>
        <div className="flex flex-wrap gap-1">
          {p.enabled_channels.map((c) => <span key={c} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{c}</span>)}
        </div>
      </div>
      <div className="mb-3">
        <p className="text-[10px] font-medium text-gray-500 mb-1">Categories</p>
        <div className="flex flex-wrap gap-1">
          {p.enabled_categories.map((c) => <span key={c} className="rounded bg-green-50 px-1.5 py-0.5 text-[10px] text-green-700 dark:bg-green-900 dark:text-green-200">{c}</span>)}
        </div>
      </div>
      {p.quiet_hours_start !== null && (
        <p className="text-[10px] text-gray-400">🌙 Quiet hours: {p.quiet_hours_start}:00 — {p.quiet_hours_end}:00</p>
      )}
    </div>
  );
}
