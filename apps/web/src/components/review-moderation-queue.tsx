"use client";

interface FlaggedReview { id: string; text: string; rating: number; flags: { type: string; detail: string }[]; action: string; }
interface ReviewModerationQueueProps { reviews: FlaggedReview[]; onApprove: (id: string) => void; onReject: (id: string) => void; }

export function ReviewModerationQueue({ reviews, onApprove, onReject }: ReviewModerationQueueProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Moderation Queue</h2>
        <span className="rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
          {reviews.length} pending
        </span>
      </div>
      {reviews.map(r => (
        <div key={r.id} className="rounded-lg border p-4 dark:border-gray-700">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm text-yellow-500">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
              </div>
              <p className="mt-1 text-sm">{r.text}</p>
              <div className="mt-2 flex gap-1">
                {r.flags.map((f, i) => (
                  <span key={i} className="rounded bg-red-50 px-1.5 py-0.5 text-xs text-red-600 dark:bg-red-900/20">{f.type}</span>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-3 flex gap-2">
            <button onClick={() => onApprove(r.id)} className="rounded bg-green-600 px-3 py-1 text-xs text-white">Approve</button>
            <button onClick={() => onReject(r.id)} className="rounded bg-red-600 px-3 py-1 text-xs text-white">Reject</button>
          </div>
        </div>
      ))}
    </div>
  );
}
