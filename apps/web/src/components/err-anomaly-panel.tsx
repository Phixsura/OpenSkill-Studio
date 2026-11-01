"use client";
interface ErrAnomalyPanelProps { anomaly: boolean; latest: number; mean: number; zScore: number; trend: string; }
export function ErrAnomalyPanel({ anomaly, latest, mean, zScore, trend }: ErrAnomalyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔴 Error Anomaly</h3>
        <span className={`text-xs font-bold ${anomaly ? "text-red-500" : "text-green-600"}`}>
          {anomaly ? `⚠ ANOMALY (${zScore}σ)` : "✅ Normal"} · trend: {trend}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Current</span><div className={`font-bold text-lg ${anomaly ? "text-red-500" : ""}`}>{latest}%</div></div>
        <div><span className="text-gray-400">Mean</span><div className="font-bold text-lg">{mean}%</div></div>
        <div><span className="text-gray-400">Z-Score</span><div className="font-bold text-lg">{zScore}σ</div></div>
      </div>
    </div>
  );
}
