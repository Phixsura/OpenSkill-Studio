"use client";

interface AnomalyPoint { index: number; value: number; zScore: number; }
interface AnomalyScorePanelProps { anomalies: AnomalyPoint[]; mean: number; std: number; threshold: number; total: number; }

export function AnomalyScorePanel({ anomalies, mean, std, threshold, total }: AnomalyScorePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Anomaly Detection</h3>
        <span className={`text-xs ${anomalies.length > 0 ? "text-red-500" : "text-green-600"}`}>
          {anomalies.length > 0 ? `⚠ ${anomalies.length} anomalies` : "✅ Normal"} / {total} points
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Mean</div><div className="font-bold">{mean}</div></div>
        <div><div className="text-gray-400">Std Dev</div><div className="font-bold">{std}</div></div>
        <div><div className="text-gray-400">Threshold</div><div className="font-bold">{threshold}σ</div></div>
      </div>
      {anomalies.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {anomalies.map(a => (
            <div key={a.index} className="flex justify-between px-4 py-1.5 text-xs text-red-600">
              <span>Index {a.index}</span>
              <span>{a.value} ({a.zScore}σ)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
