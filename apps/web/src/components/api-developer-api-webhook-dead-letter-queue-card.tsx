"use client";

interface LetterInfo { letter_id: string; event_type: string; destination: string; failure_reason: string; retry_count: number; requeued: boolean; }
interface Props { letters: LetterInfo[]; totalCount: number; byDestination: Record<string, number>; appName: string; }

export default function APIDeveloperAPIWebhookDeadLetterQueueCard({ letters, totalCount, byDestination, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💀 Dead Letter Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {totalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{totalCount}</span>}
      </div>
      {Object.keys(byDestination).length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1">
          {Object.entries(byDestination).map(([dest, count]) => (
            <span key={dest} className="rounded bg-red-50 px-1.5 py-0.5 text-[9px] text-red-600 dark:bg-red-900/30 dark:text-red-300">{new URL(dest).hostname}: {count}</span>
          ))}
        </div>
      )}
      {letters.length === 0 ? (
        <p className="text-center text-sm text-gray-400">Queue empty</p>
      ) : (
        <div className="space-y-1">
          {letters.map((l) => (
            <div key={l.letter_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="text-gray-700 dark:text-gray-300">{l.event_type}</span>
                {l.requeued && <span className="text-[9px] text-blue-500">requeued</span>}
              </div>
              <span className="text-gray-400">{l.failure_reason} · {l.retry_count}x</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
