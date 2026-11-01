"use client";

interface Anomaly { day: number; cost: number; deviation: number; }
interface CostAnomalyChartProps { mean: number; std: number; upperBound: number;
  anomalies: Anomaly[]; status: string; projectedTotal?: number; }

export function CostAnomalyChart({ mean, upperBound, anomalies, status, projectedTotal }: CostAnomalyChartProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost Anomaly Detection</h3>
        <span className={`text-xs font-bold ${status === "alert" ? "text-red-500" : "text-green-600"}`}>
          {status === "alert" ? `⚠ ${anomalies.length} anomalies` : "✅ Normal"}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Daily Avg</div><div className="font-bold text-lg">${mean}</div></div>
        <div><div className="text-gray-400">Upper Bound</div><div className="font-bold text-lg">${upperBound}</div></div>
        {projectedTotal != null && (
          <div><div className="text-gray-400">Projected</div><div className="font-bold text-lg">${projectedTotal.toLocaleString()}</div></div>
        )}
      </div>
      {anomalies.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {anomalies.map(a => (
            <div key={a.day} className="flex justify-between px-4 py-1.5 text-xs text-red-600">
              <span>Day {a.day}</span>
              <span>${a.cost} ({a.deviation}σ)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
