"use client";

interface Entry { id: string; version: string; title: string; type: string; publishedAt: string; }
interface Props { entries: Entry[]; unreadCount: number; appName: string; }

const typeColors: Record<string, string> = {
  feature: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  fix: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  deprecation: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  breaking: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  security: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelogCard({ entries, unreadCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📰 API Changelog</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unreadCount > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[10px] font-bold text-white">{unreadCount} new</span>}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelog entries</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div key={e.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{e.title}</span>
                <span className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${typeColors[e.type] ?? ""}`}>{e.type}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">v{e.version} · {e.publishedAt}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
