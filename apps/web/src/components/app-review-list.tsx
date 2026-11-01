"use client";

interface Review { userId: string; rating: number; title: string; body: string; }
interface ReviewSummary { count: number; avgDisplay: string; distribution: Record<number, number>; }
interface AppReviewListProps { reviews: Review[]; summary: ReviewSummary; }

export function AppReviewList({ reviews, summary }: AppReviewListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">⭐ Reviews</h3>
          <span className="text-sm font-bold">{summary.avgDisplay} · {summary.count} reviews</span>
        </div>
        <div className="flex gap-1 mt-2">
          {[5, 4, 3, 2, 1].map(star => (
            <div key={star} className="flex items-center gap-1 text-xs">
              <span>{star}★</span>
              <div className="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded">
                <div className="h-full bg-yellow-500 rounded"
                     style={{ width: `${(summary.distribution[star] || 0) / Math.max(summary.count, 1) * 100}%` }} />
              </div>
              <span className="text-gray-400">{summary.distribution[star] || 0}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {reviews.map((r, i) => (
          <div key={i} className="px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-yellow-500">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
              <span className="text-sm font-medium">{r.title}</span>
            </div>
            {r.body && <p className="text-xs text-gray-500">{r.body}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
