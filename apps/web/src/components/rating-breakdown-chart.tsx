"use client";

interface RatingBreakdownChartProps { avg: number; total: number;
  distribution: Record<number, number>; trend: string; fiveStarPct: number; }

const trendIcon: Record<string, string> = { improving: "📈", declining: "📉", stable: "➡️" };

export function RatingBreakdownChart({ avg, total, distribution, trend, fiveStarPct }: RatingBreakdownChartProps) {
  const maxCount = Math.max(...Object.values(distribution), 1);
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <p className="text-4xl font-black">{avg}</p>
          <p className="text-xs text-yellow-500">{"★".repeat(Math.round(avg))}</p>
          <p className="text-xs text-gray-400">{total} ratings</p>
        </div>
        <div className="flex-1 space-y-1">
          {[5, 4, 3, 2, 1].map(star => (
            <div key={star} className="flex items-center gap-2">
              <span className="w-4 text-right text-xs">{star}</span>
              <div className="h-2.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-yellow-400"
                  style={{ width: `${((distribution[star] ?? 0) / maxCount) * 100}%` }} />
              </div>
              <span className="w-8 text-right text-xs text-gray-400">{distribution[star] ?? 0}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{fiveStarPct}% five-star</span>
        <span>{trendIcon[trend]} {trend}</span>
      </div>
    </div>
  );
}
