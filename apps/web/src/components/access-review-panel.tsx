"use client";

interface ReviewItem { userId: string; role: string; lastActiveDays: number; decision: string; }
interface AccessReviewPanelProps { items: ReviewItem[]; reviewed: number; total: number;
  onDecide: (userId: string, decision: string) => void; }

export function AccessReviewPanel({ items, reviewed, total, onDecide }: AccessReviewPanelProps) {
  const pct = Math.round((reviewed / Math.max(total, 1)) * 100);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Access Review</h3>
        <span className="text-xs text-gray-400">{reviewed}/{total} reviewed ({pct}%)</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map(i => (
          <div key={i.userId} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-mono">{i.userId}</span>
              <span className="text-xs text-gray-400 ml-2">{i.role} · {i.lastActiveDays}d inactive</span>
            </div>
            {i.decision === "pending" ? (
              <div className="flex gap-1">
                <button onClick={() => onDecide(i.userId, "approve")} className="px-2 py-0.5 text-xs bg-green-500 text-white rounded">✓</button>
                <button onClick={() => onDecide(i.userId, "revoke")} className="px-2 py-0.5 text-xs bg-red-500 text-white rounded">✗</button>
              </div>
            ) : (
              <span className={`text-xs ${i.decision === "approve" ? "text-green-600" : "text-red-500"}`}>{i.decision}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
