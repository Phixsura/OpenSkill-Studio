"use client";

interface RatingSummaryProps { average: number; averageDisplay: string; count: number;
  distribution: Record<number, number>; sentiment: string; }

export function RatingSummary({ average, averageDisplay, count, distribution, sentiment }: RatingSummaryProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center gap-4 mb-4">
        <div className="text-center">
          <p className="text-4xl font-bold">{average}</p>
          <p className="text-sm text-yellow-500">{"★".repeat(Math.round(average))}{"☆".repeat(5 - Math.round(average))}</p>
          <p className="text-xs text-gray-400">{count} reviews</p>
        </div>
        <div className="flex-1 space-y-1">
          {[5, 4, 3, 2, 1].map(star => {
            const pct = count > 0 ? ((distribution[star] || 0) / count) * 100 : 0;
            return (
              <div key={star} className="flex items-center gap-2 text-xs">
                <span className="w-3">{star}</span>
                <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${pct}%` }} />
                </div>
                <span className="w-6 text-gray-400 text-right">{distribution[star] || 0}</span>
              </div>
            );
          })}
        </div>
      </div>
      <p className={`text-xs text-center capitalize ${sentiment === "positive" ? "text-green-600" : sentiment === "negative" ? "text-red-500" : "text-yellow-600"}`}>
        {sentiment} sentiment
      </p>
    </div>
  );
}
