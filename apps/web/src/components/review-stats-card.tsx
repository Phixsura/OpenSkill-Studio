"use client";

interface ReviewStatsCardProps { total: number; avgRating: number; stars: string;
  distribution: Record<number, number>; nps: number; recommendationPct: number;
  sentiment: { positive: number; neutral: number; negative: number }; }

export function ReviewStatsCard({ total, avgRating, stars, distribution, nps, recommendationPct, sentiment }: ReviewStatsCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <p className="text-4xl font-bold">{avgRating}</p>
          <p className="text-yellow-500">{stars}</p>
          <p className="text-xs text-gray-400">{total} reviews</p>
        </div>
        <div className="flex-1 space-y-1">
          {[5, 4, 3, 2, 1].map(star => (
            <div key={star} className="flex items-center gap-2">
              <span className="w-3 text-xs text-right">{star}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-yellow-500"
                  style={{ width: `${(distribution[star] ?? 0) / Math.max(total, 1) * 100}%` }} />
              </div>
              <span className="w-6 text-xs text-gray-400 text-right">{distribution[star] ?? 0}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-3 text-center text-xs">
        <div><p className="font-bold text-green-600">{sentiment.positive}</p><p className="text-gray-400">Positive</p></div>
        <div><p className="font-bold text-gray-500">{sentiment.neutral}</p><p className="text-gray-400">Neutral</p></div>
        <div><p className="font-bold text-red-600">{sentiment.negative}</p><p className="text-gray-400">Negative</p></div>
      </div>
      <div className="mt-3 flex justify-around text-xs text-gray-400">
        <span>NPS: <strong className={nps >= 0 ? "text-green-600" : "text-red-600"}>{nps}</strong></span>
        <span>{recommendationPct}% recommend</span>
      </div>
    </div>
  );
}
