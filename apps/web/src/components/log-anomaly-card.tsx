"use client";

interface Anomaly { index: number; count: number; zScore: number; type: string; }
interface LogAnomalyCardProps { anomalies: Anomaly[]; mean: number; std: number;
  checked: number; hasAnomaly: boolean; }

export function LogAnomalyCard({ anomalies, mean, std, checked, hasAnomaly }: LogAnomalyCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Log Anomalies</h3>
        <span className={`text-xs ${hasAnomaly ? "text-red-500" : "text-green-600"}`}>
          {hasAnomaly ? `⚠ ${anomalies.length} detected` : "✅ Normal"}
        </span>
      </div>
      <div className="p-3 text-xs text-gray-400 border-b dark:border-gray-700">
        {checked} periods · mean: {mean} · std: {std}
      </div>
      {anomalies.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {anomalies.map(a => (
            <div key={a.index} className="flex justify-between px-4 py-1.5 text-xs">
              <span>Period {a.index}: <span className="font-bold">{a.count}</span></span>
              <span className={a.type === "spike" ? "text-red-500" : "text-blue-500"}>
                {a.type === "spike" ? "📈" : "📉"} z={a.zScore}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
