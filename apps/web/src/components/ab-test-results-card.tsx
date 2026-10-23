"use client";

interface VariantResult { name: string; views: number; conversions: number; rate: number; }
interface AbTestResultsCardProps { experimentName: string; results: VariantResult[];
  winner: string; bestRate: number; }

export function AbTestResultsCard({ experimentName, results, winner, bestRate }: AbTestResultsCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 {experimentName}</h3>
        <span className="text-xs text-green-600 font-medium">Winner: {winner} ({bestRate}%)</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(v => {
          const isWinner = v.name === winner;
          return (
            <div key={v.name} className={`px-4 py-3 ${isWinner ? "bg-green-50 dark:bg-green-900/10" : ""}`}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{v.name} {isWinner && "🏆"}</span>
                <span className="text-xs font-mono">{v.rate}% conversion</span>
              </div>
              <div className="flex gap-4 text-xs text-gray-400">
                <span>{v.views.toLocaleString()} views</span>
                <span>{v.conversions.toLocaleString()} conversions</span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full mt-1">
                <div className={`h-full rounded-full ${isWinner ? "bg-green-500" : "bg-blue-400"}`}
                  style={{ width: `${Math.min(v.rate * 5, 100)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
