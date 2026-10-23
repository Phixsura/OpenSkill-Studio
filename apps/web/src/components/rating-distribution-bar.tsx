"use client";

interface RatingBar { stars: number; count: number; pct: number; }
interface RatingDistributionBarProps { bars: RatingBar[]; avg: number; total: number; }

export function RatingDistributionBar({ bars, avg, total }: RatingDistributionBarProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <p className="text-3xl font-bold">{avg.toFixed(1)}</p>
          <div className="flex text-yellow-400">
            {Array.from({ length: 5 }, (_, i) => <span key={i}>{i < Math.round(avg) ? "★" : "☆"}</span>)}
          </div>
          <p className="text-xs text-gray-400">{total.toLocaleString()} reviews</p>
        </div>
        <div className="flex-1 space-y-1">
          {bars.map(b => (
            <div key={b.stars} className="flex items-center gap-2">
              <span className="w-4 text-xs text-gray-500">{b.stars}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-yellow-400" style={{ width: `${b.pct}%` }} />
              </div>
              <span className="w-8 text-right text-xs text-gray-400">{b.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
