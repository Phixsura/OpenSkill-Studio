"use client";

interface ModeratedReview { safeBody: string; rating: number; status: string; flags: string[]; }
interface ReviewModerationPanelProps { reviews: ModeratedReview[];
  approvalRate: number; onApprove: (idx: number) => void; onReject: (idx: number) => void; }

const STATUS_BADGE: Record<string, string> = {
  approved: "bg-green-100 text-green-700", flagged: "bg-yellow-100 text-yellow-700",
  rejected: "bg-red-100 text-red-700",
};

export function ReviewModerationPanel({ reviews, approvalRate, onApprove, onReject }: ReviewModerationPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Review Moderation</h3>
        <span className="text-xs text-gray-400">{approvalRate}% approval rate</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {reviews.map((r, i) => (
          <div key={i} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-yellow-500">{"★".repeat(r.rating)}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${STATUS_BADGE[r.status] || ""}`}>{r.status}</span>
              </div>
              {r.status === "flagged" && (
                <div className="flex gap-1">
                  <button onClick={() => onApprove(i)} className="text-xs px-2 py-0.5 bg-green-600 text-white rounded">Approve</button>
                  <button onClick={() => onReject(i)} className="text-xs px-2 py-0.5 bg-red-600 text-white rounded">Reject</button>
                </div>
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300">{r.safeBody}</p>
            {r.flags.length > 0 && <p className="text-xs text-red-400 mt-1">Flags: {r.flags.join(", ")}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
