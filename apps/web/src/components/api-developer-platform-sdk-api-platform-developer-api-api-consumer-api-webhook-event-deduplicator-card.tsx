"use client";

interface Stats { checked: number; duplicates: number; duplicate_rate: number; }
interface Props { stats: Stats; windowMinutes: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicatorCard({ stats, windowMinutes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Event Deduplicator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {windowMinutes}m window</p>
        </div>
        <span className="text-[10px] text-gray-400">{stats.duplicate_rate}% dupes</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.checked.toLocaleString()}</div><div className="text-gray-400">Checked</div></div>
        <div><div className="font-semibold text-amber-600 dark:text-amber-400">{stats.duplicates.toLocaleString()}</div><div className="text-gray-400">Duplicates</div></div>
      </div>
    </div>
  );
}
