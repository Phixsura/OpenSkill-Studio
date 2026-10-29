"use client";

interface DlqInfo { entry_id: string; consumer_id: string; reason: string; attempts: number; last_status_code: number; requeued: boolean; }
interface Props { entries: DlqInfo[]; totalCount: number; reasonCounts: Record<string, number>; appName: string; }

const reasonEmoji: Record<string, string> = { max_retries: "🔄", timeout: "⏱️", connection_error: "🔌", invalid_response: "❌", circuit_open: "⚡" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueueCard({ entries, totalCount, reasonCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💀 Dead Letter Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${totalCount > 0 ? "text-red-600 dark:text-red-400" : "text-green-600 dark:text-green-400"}`}>{totalCount}</span>
      </div>
      {Object.keys(reasonCounts).length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2 text-[10px]">
          {Object.entries(reasonCounts).map(([r, c]) => (
            <span key={r} className="text-gray-500">{reasonEmoji[r] ?? "•"} {r}: {c}</span>
          ))}
        </div>
      )}
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">Queue empty</p>
      ) : (
        <div className="space-y-1">
          {entries.slice(0, 5).map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.consumer_id}</span>
              <span className="text-gray-400">{e.reason} · {e.attempts}× · {e.requeued ? "♻️" : e.last_status_code}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
