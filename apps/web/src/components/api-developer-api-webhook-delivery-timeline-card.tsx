"use client";

interface EntryInfo { delivery_id: string; event_type: string; destination: string; status: string; latency_ms: number; }
interface Props { entries: EntryInfo[]; totalCount: number; failureCount: number; appName: string; }

const sDot: Record<string, string> = { success: "bg-green-500", failure: "bg-red-500", timeout: "bg-orange-500", retry: "bg-yellow-500" };

export default function APIDeveloperAPIWebhookDeliveryTimelineCard({ entries, totalCount, failureCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Delivery Timeline</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{totalCount} total</span>
          {failureCount > 0 && <p className="text-[10px] text-red-500">{failureCount} failures</p>}
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deliveries</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.delivery_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${sDot[e.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{e.event_type}</span>
              </div>
              <span className="text-gray-400">{e.status} · {e.latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
