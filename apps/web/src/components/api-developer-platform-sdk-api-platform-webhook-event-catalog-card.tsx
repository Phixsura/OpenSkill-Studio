"use client";

interface EventInfo { event_type: string; category: string; description: string; schema_version: string; subscribers: number; }
interface Props { events: EventInfo[]; categoryCounts: Record<string, number>; appName: string; }

const catColor: Record<string, string> = { orders: "bg-blue-100 text-blue-700", users: "bg-green-100 text-green-700", payments: "bg-purple-100 text-purple-700", system: "bg-gray-100 text-gray-600" };

export default function APIDeveloperPlatformSDKApiPlatformWebhookEventCatalogCard({ events, categoryCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 Event Catalog</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {events.length} events</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(categoryCounts).map(([cat, count]) => (
          <span key={cat} className={`rounded px-1.5 py-0.5 text-[10px] ${catColor[cat] ?? "bg-gray-100 text-gray-600"}`}>{cat}: {count}</span>
        ))}
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No events in catalog</p>
      ) : (
        <div className="space-y-1">
          {events.slice(0, 6).map((e) => (
            <div key={e.event_type} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-700 dark:text-gray-300">{e.event_type}</span>
              </div>
              <span className="text-[10px] text-gray-400">v{e.schema_version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
