"use client";

interface TypeInfo { event_type: string; description: string; schema_version: string; category: string; deprecated: boolean; }
interface Props { types: TypeInfo[]; categoryCounts: Record<string, number>; appName: string; }

const catColor: Record<string, string> = { resource: "bg-blue-100 text-blue-700", lifecycle: "bg-green-100 text-green-700", notification: "bg-purple-100 text-purple-700", system: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistryCard({ types, categoryCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Event Types</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {types.length} types</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(categoryCounts).map(([cat, count]) => (
          <span key={cat} className={`rounded px-1.5 py-0.5 text-[10px] ${catColor[cat] ?? ""}`}>{cat}: {count}</span>
        ))}
      </div>
      {types.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event types</p>
      ) : (
        <div className="space-y-1">
          {types.slice(0, 8).map((t) => (
            <div key={t.event_type} className={`flex items-center justify-between text-[11px] ${t.deprecated ? "opacity-40" : ""}`}>
              <span className="font-mono text-gray-700 dark:text-gray-300">{t.event_type}</span>
              <span className="text-[10px] text-gray-400">v{t.schema_version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
