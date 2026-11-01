"use client";

interface Review { id: string; rating: number; title: string; body: string; createdAt: string; }
interface ReviewListProps { reviews: Review[]; avgRating: number; total: number; starsDisplay: string;
  distribution: Record<number, number>; }

export function ReviewList({ reviews, avgRating, total, starsDisplay, distribution }: ReviewListProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <p className="text-3xl font-bold">{avgRating}</p>
          <p className="text-yellow-500">{starsDisplay}</p>
          <p className="text-xs text-gray-400">{total} reviews</p>
        </div>
        <div className="flex-1 space-y-1">
          {[5, 4, 3, 2, 1].map(star => (
            <div key={star} className="flex items-center gap-2">
              <span className="w-4 text-xs text-right">{star}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-yellow-500"
                  style={{ width: `${(distribution[star] ?? 0) / Math.max(total, 1) * 100}%` }} />
              </div>
              <span className="w-6 text-xs text-gray-400 text-right">{distribution[star] ?? 0}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {reviews.map(r => (
          <div key={r.id} className="py-3">
            <div className="flex items-center gap-2">
              <span className="text-yellow-500 text-xs">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
              <span className="text-sm font-medium">{r.title}</span>
            </div>
            <p className="mt-1 text-sm text-gray-500">{r.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
