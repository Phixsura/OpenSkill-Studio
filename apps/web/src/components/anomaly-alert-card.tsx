"use client";

interface Anomaly { index: number; value: number; z_score: number; type: string; deviation_pct: number; }
interface AnomalyAlertCardProps { anomalies: Anomaly[]; mean: number; stdDev: number; anomalyRate: number; }

export function AnomalyAlertCard({ anomalies, mean, stdDev, anomalyRate }: AnomalyAlertCardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Usage Anomalies</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${anomalies.length === 0 ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {anomalies.length === 0 ? "All normal" : `${anomalies.length} detected`}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center text-sm">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="font-bold">{mean}</p><p className="text-xs text-gray-400">Mean</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="font-bold">±{stdDev}</p><p className="text-xs text-gray-400">Std Dev</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="font-bold">{anomalyRate}%</p><p className="text-xs text-gray-400">Anomaly Rate</p>
        </div>
      </div>
      {anomalies.length > 0 && (
        <div className="space-y-1.5">
          {anomalies.map(a => (
            <div key={a.index} className={`flex items-center justify-between rounded border px-3 py-2 ${a.type === "spike" ? "border-red-200 dark:border-red-800" : "border-blue-200 dark:border-blue-800"}`}>
              <div className="flex items-center gap-2">
                <span>{a.type === "spike" ? "📈" : "📉"}</span>
                <span className="text-sm">Point #{a.index}: <strong>{a.value}</strong></span>
              </div>
              <span className="text-xs text-gray-400">z={a.z_score} ({a.deviation_pct}% off)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
