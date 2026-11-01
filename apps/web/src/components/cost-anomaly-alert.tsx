"use client";

interface Anomaly { day: number; cost: number; zScore: number; direction: string; }
interface CostAnomalyAlertProps { anomalies: Anomaly[]; mean: number; std: number;
  hasAnomaly: boolean; potentialSavings: string; }

export function CostAnomalyAlert({ anomalies, mean, std, hasAnomaly, potentialSavings }: CostAnomalyAlertProps) {
  return (
    <div className={`rounded-xl border overflow-hidden ${hasAnomaly ? "border-red-300 dark:border-red-800" : "border-gray-200 dark:border-gray-700"}`}>
      <div className={`flex items-center justify-between p-4 border-b ${hasAnomaly ? "bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800" : "dark:border-gray-700"}`}>
        <h3 className="font-semibold text-sm">💸 Cost Anomalies</h3>
        <span className={`text-xs ${hasAnomaly ? "text-red-600" : "text-green-600"}`}>
          {hasAnomaly ? `⚠ ${anomalies.length} detected` : "✅ Normal"}
        </span>
      </div>
      <div className="p-3 text-xs text-gray-400 border-b dark:border-gray-700">
        Mean: ${mean}/day · Std: ${std} · Potential savings: {potentialSavings}
      </div>
      {anomalies.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {anomalies.map((a, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
              <span>Day {a.day}: <span className="font-bold">${a.cost}</span></span>
              <span className={a.direction === "spike" ? "text-red-500" : "text-blue-500"}>
                {a.direction === "spike" ? "📈" : "📉"} z={a.zScore}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
