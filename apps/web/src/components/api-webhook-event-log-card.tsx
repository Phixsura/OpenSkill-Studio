"use client";

interface EventLogInfo { event_id: string; event_type: string; destination_count: number; payload_size: number; }
interface Props { events: EventLogInfo[]; totalCount: number; appName: string; }

function fmt(b: number): string { if (b < 1024) return `${b}B`; return `${(b/1024).toFixed(1)}KB`; }

export default function APIWebhookEventLogCard({ events, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Event Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalCount} events</span>
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No events logged</p>
      ) : (
        <div className="space-y-1">
          {events.map((e) => (
            <div key={e.event_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.event_type}</span>
              <span className="text-gray-400">{e.destination_count} dest · {fmt(e.payload_size)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
