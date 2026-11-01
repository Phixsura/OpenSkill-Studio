"use client";

interface Stats { totalEntries: number; oldestAgeDays: number; storageMb: number; dueForDeletion: number; }
interface Props { stats: Stats; retentionDays: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetentionCard({ stats, retentionDays, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Access Log Retention</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Retain: {retentionDays}d</p>
      </div>
      <div className="grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{stats.totalEntries.toLocaleString()}</div><div className="text-[10px] text-gray-400">Total Entries</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{stats.storageMb} MB</div><div className="text-[10px] text-gray-400">Storage</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{stats.oldestAgeDays}d</div><div className="text-[10px] text-gray-400">Oldest</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${stats.dueForDeletion > 0 ? "text-amber-600" : "text-green-600"}`}>{stats.dueForDeletion}</div><div className="text-[10px] text-gray-400">Due Delete</div></div>
      </div>
    </div>
  );
}
