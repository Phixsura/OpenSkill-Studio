"use client";

interface EventInfo { event_id: string; name: string; category: string; deprecated: boolean; field_count: number; }
interface Props { events: EventInfo[]; categories: string[]; deprecatedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalogCard({ events, categories, deprecatedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 Event Catalog</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {events.length} events · {categories.length} categories</p>
        </div>
        {deprecatedCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">⚠️ {deprecatedCount} deprecated</span>}
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No events registered</p>
      ) : (
        <div className="space-y-1">
          {events.map((e) => (
            <div key={e.event_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={e.deprecated ? "text-gray-400 line-through" : "font-mono text-gray-700 dark:text-gray-300"}>{e.name}</span>
              </div>
              <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{e.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
