"use client";

interface FilterInfo { filter_id: string; destination: string; include_events: string[]; exclude_events: string[]; matched_count: number; dropped_count: number; }
interface Props { filters: FilterInfo[]; appName: string; }

export default function APIDeveloperAPIApiWebhookEventFilterCard({ filters, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Event Filters</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {filters.length} filters</p>
      </div>
      {filters.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event filters</p>
      ) : (
        <div className="space-y-2">
          {filters.map((f) => (
            <div key={f.filter_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{f.filter_id}</span>
                <div className="flex gap-2 text-[10px]">
                  <span className="text-green-600">{f.matched_count} matched</span>
                  <span className="text-red-500">{f.dropped_count} dropped</span>
                </div>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {f.include_events.map((e) => <span key={e} className="rounded bg-green-50 px-1 py-0.5 text-[9px] text-green-700">+{e}</span>)}
                {f.exclude_events.map((e) => <span key={e} className="rounded bg-red-50 px-1 py-0.5 text-[9px] text-red-700">-{e}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
