"use client";

interface DLQEntry { id: string; eventType: string; error: string; attempts: number; lastFailedAt: string; status: string; }
interface Props { entries: DLQEntry[]; counts: { pending: number; requeued: number; discarded: number }; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueueCard({ entries, counts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💀 Dead Letter Queue</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20">
          <div className="font-bold text-red-600">{counts.pending}</div>
          <div className="text-[10px] text-gray-400">Pending</div>
        </div>
        <div className="rounded bg-blue-50 p-1.5 dark:bg-blue-900/20">
          <div className="font-bold text-blue-600">{counts.requeued}</div>
          <div className="text-[10px] text-gray-400">Requeued</div>
        </div>
        <div className="rounded bg-gray-100 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-500">{counts.discarded}</div>
          <div className="text-[10px] text-gray-400">Discarded</div>
        </div>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">Queue empty</p>
      ) : (
        <div className="space-y-1">
          {entries.slice(0, 5).map((e) => (
            <div key={e.id} className="rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex justify-between">
                <span className="font-medium text-gray-700 dark:text-gray-300">{e.eventType}</span>
                <span className="text-gray-400">{e.attempts} attempts</span>
              </div>
              <div className="text-red-400 truncate">{e.error}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
