"use client";

interface EntryInfo { event_id: string; event_type: string; destination: string; status: string; payload_size_bytes: number; }
interface Props { entries: EntryInfo[]; summary: Record<string, number>; totalCount: number; appName: string; }

const sDot: Record<string, string> = { delivered: "bg-green-500", failed: "bg-red-500", pending: "bg-gray-400", retrying: "bg-yellow-500" };

export default function APIDeveloperAPIApiWebhookEventLogCard({ entries, summary, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Event Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalCount.toLocaleString()} events</p>
        </div>
        <div className="flex gap-2 text-[10px]">
          {Object.entries(summary).filter(([,v]) => v > 0).map(([s, c]) => (
            <span key={s} className="text-gray-400">{s}: {c}</span>
          ))}
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No events</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.event_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${sDot[e.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{e.event_type}</span>
              </div>
              <span className="text-gray-400">{e.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
