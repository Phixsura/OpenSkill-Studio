"use client";

interface ReviewSummaryCardProps { avgRating: number; total: number; distribution: Record<number, number>;
  sentiment: string; positivePct: number; }

const sentimentIcon: Record<string, string> = { positive: "😊", mixed: "😐", negative: "😞", neutral: "—" };

export function ReviewSummaryCard({ avgRating, total, distribution, sentiment, positivePct }: ReviewSummaryCardProps) {
  const maxCount = Math.max(...Object.values(distribution), 1);
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <p className="text-3xl font-black">{avgRating}</p>
          <p className="text-xs text-yellow-500">{"★".repeat(Math.round(avgRating))}{"☆".repeat(5 - Math.round(avgRating))}</p>
          <p className="text-xs text-gray-400">{total} reviews</p>
        </div>
        <div className="flex-1 space-y-1">
          {[5, 4, 3, 2, 1].map(star => (
            <div key={star} className="flex items-center gap-2">
              <span className="w-4 text-right text-xs text-gray-400">{star}</span>
              <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-yellow-400"
                  style={{ width: `${((distribution[star] ?? 0) / maxCount) * 100}%` }} />
              </div>
              <span className="w-6 text-right text-xs text-gray-400">{distribution[star] ?? 0}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="flex items-center justify-between text-sm">
        <span>{sentimentIcon[sentiment]} {sentiment}</span>
        <span className="text-gray-400">{positivePct}% positive</span>
      </div>
    </div>
  );
}
