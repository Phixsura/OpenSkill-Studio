"use client";

interface FilterInfo { filter_id: string; event_type: string; field_path: string; operator: string; value: string; enabled: boolean; }
interface Props { filters: FilterInfo[]; appName: string; }

export default function APIWebhookEventFilterCard({ filters, appName }: Props) {
  const enabled = filters.filter((f) => f.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔽 Event Filters</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{enabled}/{filters.length} active</span>
      </div>
      {filters.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event filters</p>
      ) : (
        <div className="space-y-1">
          {filters.map((f) => (
            <div key={f.filter_id} className={`flex items-center justify-between text-[11px] ${!f.enabled ? "opacity-50" : ""}`}>
              <span className="font-mono text-gray-700 dark:text-gray-300">{f.field_path} {f.operator} {f.value}</span>
              <span className="text-gray-400">{f.event_type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
