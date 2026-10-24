"use client";

interface Anomaly { metric: string; latest: number; mean: number; zScore: number; type: string; }
interface AnomalyDetectionCardProps { anomalies: Anomaly[]; metricsChecked: number; hasAnomaly: boolean; }

export function AnomalyDetectionCard({ anomalies, metricsChecked, hasAnomaly }: AnomalyDetectionCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔮 Anomaly Detection</h3>
        <span className={`text-xs ${hasAnomaly ? "text-red-500" : "text-green-600"}`}>
          {hasAnomaly ? `⚠ ${anomalies.length} anomalies` : "✅ Normal"} · {metricsChecked} checked
        </span>
      </div>
      {anomalies.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {anomalies.map(a => (
            <div key={a.metric} className="flex justify-between px-4 py-2 text-xs">
              <span className="font-mono text-red-600">{a.metric}: {a.latest}</span>
              <span className="text-gray-400">mean {a.mean} · z={a.zScore} {a.type === "high" ? "📈" : "📉"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
