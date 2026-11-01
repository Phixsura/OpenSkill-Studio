"use client";

interface CostAnomalyAlerterProps { anomaly: boolean; current: number; mean: number;
  zScore: number; type: string; alert: boolean; spikes: number; }

export function CostAnomalyAlerter({ anomaly, current, mean, zScore, type, alert, spikes }: CostAnomalyAlerterProps) {
  return (
    <div className={`rounded-xl border overflow-hidden ${alert ? "border-red-500 dark:border-red-800" : "dark:border-gray-700"}`}>
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${alert ? "bg-red-50 dark:bg-red-900/10" : ""}`}>
        <h3 className="font-semibold">💸 Cost Alert</h3>
        <span className={`text-xs font-medium ${alert ? "text-red-600" : "text-green-600"}`}>
          {alert ? `🚨 Spike! $${current} (z=${zScore})` : "✅ Normal"}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-900 p-2 text-center">
          <div className="text-sm font-bold">${current}</div>
          <div className="text-[9px] text-gray-400">Current</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center">
          <div className="text-sm font-bold">${mean}</div>
          <div className="text-[9px] text-gray-400">Average</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center">
          <div className={`text-sm font-bold ${anomaly ? "text-red-600" : ""}`}>{zScore}</div>
          <div className="text-[9px] text-gray-400">Z-Score</div>
        </div>
      </div>
    </div>
  );
}
