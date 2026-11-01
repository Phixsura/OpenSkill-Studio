"use client";

interface HighCardMetric { metric: string; series: number; labels: number; recommendation: string; }
interface CardinalityAnalyzerProps { totalMetrics: number; totalSeries: number;
  highCardCount: number; highCardinality: HighCardMetric[]; costFactor: number; }

export function CardinalityAnalyzer({ totalMetrics, totalSeries, highCardCount, highCardinality, costFactor }: CardinalityAnalyzerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Metric Cardinality</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalSeries.toLocaleString()} series</span>
          {highCardCount > 0 && <span className="text-red-500">⚠ {highCardCount} high-cardinality</span>}
        </div>
      </div>
      {highCardinality.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {highCardinality.map(h => (
            <div key={h.metric} className="px-4 py-2 text-xs">
              <div className="flex justify-between">
                <span className="font-mono text-red-600">{h.metric}</span>
                <span className="text-gray-400">{h.series.toLocaleString()} series</span>
              </div>
              <div className="text-[10px] text-yellow-600 mt-0.5">💡 {h.recommendation}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
