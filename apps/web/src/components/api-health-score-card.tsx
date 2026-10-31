"use client";

interface DimensionInfo {
  dimension_id: string;
  name: string;
  weight: number;
  score: number;
}

interface APIHealthScoreCardProps {
  dimensions: DimensionInfo[];
  compositeScore: number;
  appName: string;
}

export default function APIHealthScoreCard({ dimensions, compositeScore, appName }: APIHealthScoreCardProps) {
  const scoreColor = compositeScore >= 90 ? "text-green-600" : compositeScore >= 70 ? "text-yellow-600" : "text-red-500";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💚 Health Score</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-2xl font-bold ${scoreColor}`}>{compositeScore}</span>
      </div>

      {dimensions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health dimensions</p>
      ) : (
        <div className="space-y-2">
          {dimensions.map((d) => {
            const barColor = d.score >= 90 ? "bg-green-500" : d.score >= 70 ? "bg-yellow-500" : "bg-red-500";
            return (
              <div key={d.dimension_id}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{d.name}</span>
                  <span className="text-gray-400">{d.score}/100 (w{d.weight})</span>
                </div>
                <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className={`h-1 rounded-full ${barColor}`} style={{ width: `${d.score}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
