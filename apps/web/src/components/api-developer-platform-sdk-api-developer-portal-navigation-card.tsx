"use client";

interface NavInfo { item_id: string; label: string; path: string; icon: string; children_count: number; }
interface Props { items: NavInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperPortalNavigationCard({ items, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧭 Portal Navigation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {items.length} items</p>
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No navigation items</p>
      ) : (
        <div className="space-y-1">
          {items.map((n) => (
            <div key={n.item_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                {n.icon && <span>{n.icon}</span>}
                <span className="text-gray-700 dark:text-gray-300">{n.label}</span>
              </div>
              <div className="flex gap-2 text-[10px] text-gray-400">
                <span>{n.path}</span>
                {n.children_count > 0 && <span>{n.children_count} children</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
