"use client";

interface FeedItem { entry_id: string; version: string; title: string; change_type: string; relevant: boolean; read: boolean; }
interface Props { items: FeedItem[]; unreadCount: number; appName: string; }

const typeIcon: Record<string, string> = { feature: "✨", fix: "🐛", deprecation: "⚠️", breaking: "💥", security: "🔒", improvement: "📈" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeedCard({ items, unreadCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📰 Changelog Feed</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unreadCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{unreadCount} new</span>}
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelog entries</p>
      ) : (
        <div className="space-y-1">
          {items.map((i) => (
            <div key={i.entry_id} className={`flex items-center justify-between text-[11px] ${i.read ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span>{typeIcon[i.change_type] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{i.title}</span>
              </div>
              <span className="text-gray-400">{i.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
