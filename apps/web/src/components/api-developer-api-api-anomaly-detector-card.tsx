"use client";

interface AnomalyInfo { anomaly_id: string; endpoint: string; metric: string; severity: string; current_value: number; baseline_value: number; deviation_pct: number; }
interface Props { anomalies: AnomalyInfo[]; criticalCount: number; appName: string; }

const sevBadge: Record<string, string> = { warning: "bg-yellow-100 text-yellow-700", critical: "bg-red-100 text-red-700" };

export default function APIDeveloperAPIApiAnomalyDetectorCard({ anomalies, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Anomaly Detector</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{criticalCount} critical</span>}
      </div>
      {anomalies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No anomalies detected</p>
      ) : (
        <div className="space-y-2">
          {anomalies.map((a) => (
            <div key={a.anomaly_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${sevBadge[a.severity] ?? ""}`}>{a.severity}</span>
                  <span className="text-gray-700 dark:text-gray-300">{a.endpoint}</span>
                </div>
                <span className="text-gray-400">{a.metric}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{a.current_value} vs baseline {a.baseline_value} ({a.deviation_pct > 0 ? "+" : ""}{a.deviation_pct}%)</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
