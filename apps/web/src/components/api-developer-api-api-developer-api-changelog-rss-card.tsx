"use client";

interface ItemInfo { item_id: string; title: string; description: string; category: string; version: string; }
interface Props { items: ItemInfo[]; appName: string; }

const catBadge: Record<string, string> = { feature: "bg-green-100 text-green-700", fix: "bg-blue-100 text-blue-700", breaking: "bg-red-100 text-red-700", deprecation: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPIApiDeveloperApiChangelogRssCard({ items, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📰 Changelog Feed</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {items.length} entries</p>
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelog entries</p>
      ) : (
        <div className="space-y-2">
          {items.map((i) => (
            <div key={i.item_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${catBadge[i.category] ?? ""}`}>{i.category}</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{i.title}</span>
                </div>
                <span className="text-[10px] text-gray-400">v{i.version}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-500 truncate">{i.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
