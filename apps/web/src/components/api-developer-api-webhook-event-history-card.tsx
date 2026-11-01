"use client";

interface HistoryEntry { event_id: string; event_type: string; destination: string; status: string; latency_ms: number; }
interface Props { entries: HistoryEntry[]; totalCount: number; appName: string; }

const sDot: Record<string, string> = { delivered: "bg-green-500", failed: "bg-red-500", retrying: "bg-yellow-500", dead_letter: "bg-gray-500" };

export default function APIDeveloperAPIWebhookEventHistoryCard({ entries, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Event History</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} events</span>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No event history</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.event_id} className="flex items-center justify-between text-[11px]">
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
