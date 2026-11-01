"use client";

interface RatingDistributionProps { distribution: Record<number, number>; average: number; count: number; }

export function RatingDistribution({ distribution, average, count }: RatingDistributionProps) {
  const max = Math.max(...Object.values(distribution), 1);
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center gap-3">
        <span className="text-3xl font-bold">{average.toFixed(1)}</span>
        <div><p className="text-sm">{"★".repeat(Math.round(average))}{"☆".repeat(5 - Math.round(average))}</p>
          <p className="text-xs text-gray-500">{count} review{count !== 1 ? "s" : ""}</p></div>
      </div>
      {[5, 4, 3, 2, 1].map(stars => (
        <div key={stars} className="flex items-center gap-2 text-sm">
          <span className="w-4">{stars}</span>
          <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-2 rounded-full bg-yellow-500" style={{ width: `${((distribution[stars] || 0) / max) * 100}%` }} />
          </div>
          <span className="w-6 text-right text-xs text-gray-400">{distribution[stars] || 0}</span>
        </div>
      ))}
    </div>
  );
}
