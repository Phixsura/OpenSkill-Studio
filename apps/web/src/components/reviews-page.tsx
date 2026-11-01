"use client";

interface Review { id: string; rating: number; title: string; body: string;
  author: string; helpfulCount: number; hasResponse: boolean; }
interface ReviewsPageProps { appName: string; reviews: Review[]; total: number;
  avgRating: number; stars: string; distribution: Record<number, number>;
  sortBy: string; onSort: (sort: string) => void; onFilterRating: (rating: number | null) => void; }

export function ReviewsPage({ appName, reviews, total, avgRating, stars, distribution,
  sortBy, onSort, onFilterRating }: ReviewsPageProps) {
  return (
    <div className="space-y-5">
      <h2 className="text-lg font-bold">⭐ {appName} Reviews</h2>
      <div className="flex items-center gap-6">
        <div className="text-center">
          <p className="text-4xl font-bold">{avgRating}</p>
          <p className="text-yellow-500">{stars}</p>
          <p className="text-xs text-gray-400">{total} reviews</p>
        </div>
        <div className="flex-1 space-y-1">
          {[5, 4, 3, 2, 1].map(star => (
            <button key={star} onClick={() => onFilterRating(star)} className="flex w-full items-center gap-2">
              <span className="w-3 text-xs">{star}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-yellow-500"
                  style={{ width: `${(distribution[star] ?? 0) / Math.max(total, 1) * 100}%` }} />
              </div>
              <span className="w-6 text-xs text-gray-400 text-right">{distribution[star] ?? 0}</span>
            </button>
          ))}
        </div>
      </div>
      <select value={sortBy} onChange={e => onSort(e.target.value)}
        className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
        <option value="newest">Newest</option><option value="highest">Highest</option>
        <option value="lowest">Lowest</option><option value="helpful">Most Helpful</option>
      </select>
      <div className="divide-y dark:divide-gray-700">
        {reviews.map(r => (
          <div key={r.id} className="py-3">
            <div className="flex items-center gap-2">
              <span className="text-yellow-500 text-xs">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
              <span className="text-sm font-medium">{r.title}</span>
              {r.hasResponse && <span className="text-xs text-blue-600">💬 Response</span>}
            </div>
            <p className="mt-1 text-sm text-gray-500">{r.body}</p>
            <div className="mt-1 flex gap-3 text-xs text-gray-400">
              <span>by {r.author}</span>
              <span>👍 {r.helpfulCount}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
