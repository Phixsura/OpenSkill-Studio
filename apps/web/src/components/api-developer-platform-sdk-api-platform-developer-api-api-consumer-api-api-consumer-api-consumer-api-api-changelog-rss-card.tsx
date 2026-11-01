"use client";

interface Item { id: string; title: string; version: string; type: string; publishedAt: string; }
interface Props { items: Item[]; feedUrl: string; appName: string; }

const typeIcons: Record<string, string> = { feature: "✨", fix: "🐛", breaking: "⚠️", deprecation: "📦", security: "🔒" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRssCard({ items, feedUrl, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📰 Changelog RSS</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {items.length} entries</p>
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelog entries</p>
      ) : (
        <div className="space-y-1">
          {items.slice(0, 8).map((i) => (
            <div key={i.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span>{typeIcons[i.type] ?? "📋"}</span>
                <span className="text-gray-700 dark:text-gray-300">{i.title}</span>
              </div>
              <span className="text-[10px] text-gray-400">v{i.version}</span>
            </div>
          ))}
        </div>
      )}
      <div className="mt-2 text-[10px] text-gray-400">Feed: <code>{feedUrl}</code></div>
    </div>
  );
}
