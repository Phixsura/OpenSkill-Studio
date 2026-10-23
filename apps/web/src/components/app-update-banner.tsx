"use client";

interface AppUpdate { name: string; icon: string; current: string;
  latest: string; breaking: boolean; }
interface AppUpdateBannerProps { updates: AppUpdate[]; summary: string;
  hasBreaking: boolean; onUpdateAll: () => void; }

export function AppUpdateBanner({ updates, summary, hasBreaking, onUpdateAll }: AppUpdateBannerProps) {
  if (!updates.length) return null;
  return (
    <div className={`rounded-xl border p-4 ${hasBreaking ? "border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10" : "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/10"}`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium">{summary}</p>
        <button onClick={onUpdateAll}
          className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Update All</button>
      </div>
      <div className="flex gap-2 flex-wrap">
        {updates.map(u => (
          <span key={u.name} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-white dark:bg-gray-900 border dark:border-gray-700">
            {u.icon} {u.name} <span className="text-gray-400">{u.current} → {u.latest}</span>
            {u.breaking && <span className="text-red-500">⚠️</span>}
          </span>
        ))}
      </div>
    </div>
  );
}
