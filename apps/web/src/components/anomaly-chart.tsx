"use client";

interface Anomaly { index: number; label: string; value: number; zScore: number; direction: string; }
interface AnomalyChartProps { mean: number; std: number; totalPoints: number;
  anomalies: Anomaly[]; anomalyRate: number; }

export function AnomalyChart({ mean, std, totalPoints, anomalies, anomalyRate }: AnomalyChartProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📈 Anomaly Detection</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          anomalies.length === 0 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        }`}>{anomalies.length === 0 ? "✅ Normal" : `⚠️ ${anomalies.length} anomalies`}</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{totalPoints}</p><p className="text-xs text-gray-400">Points</p></div>
        <div><p className="text-lg font-bold">{mean}</p><p className="text-xs text-gray-400">Mean</p></div>
        <div><p className="text-lg font-bold">±{std}</p><p className="text-xs text-gray-400">Std Dev</p></div>
        <div><p className="text-lg font-bold">{anomalyRate}%</p><p className="text-xs text-gray-400">Rate</p></div>
      </div>
      {anomalies.length > 0 && (
        <div className="space-y-2">
          {anomalies.map(a => (
            <div key={a.index} className="flex items-center justify-between bg-red-50 dark:bg-red-900/10 rounded-lg px-3 py-2 text-sm">
              <div>
                <span className="font-medium">{a.label}</span>
                <span className="text-xs text-gray-400 ml-2">z={a.zScore}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono">{a.value}</span>
                <span className={`text-xs ${a.direction === "high" ? "text-red-500" : "text-blue-500"}`}>
                  {a.direction === "high" ? "↑" : "↓"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
