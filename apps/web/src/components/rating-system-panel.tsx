"use client";

interface RatingStats {
  count: number; average: number; bayesian: number;
  distribution: Record<number, number>; verifiedCount: number;
}

export function RatingSystemPanel({ stats, onRate }: {
  stats: RatingStats; onRate?: (score: number) => void;
}) {
  const maxDist = Math.max(...Object.values(stats.distribution), 1);
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="text-center">
          <span className="text-4xl font-bold">{stats.average}</span>
          <span className="text-yellow-500 text-2xl ml-1">★</span>
          <span className="text-xs text-gray-500 block">{stats.count} ratings</span>
        </div>
        <div className="flex-1 space-y-0.5">
          {[5, 4, 3, 2, 1].map((n) => (
            <div key={n} className="flex items-center gap-1 text-xs">
              <span className="w-3">{n}</span>
              <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-yellow-400 rounded-full"
                  style={{ width: `${(stats.distribution[n] / maxDist) * 100}%` }} />
              </div>
              <span className="w-6 text-right text-gray-400">{stats.distribution[n]}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="flex gap-1 justify-center">
        {[1, 2, 3, 4, 5].map((n) => (
          <button key={n} onClick={() => onRate?.(n)}
            className="text-2xl hover:scale-125 transition">{"★"}</button>
        ))}
      </div>
    </div>
  );
}
