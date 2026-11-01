"use client";

interface AnomalyInfo { request_id: string; consumer_id: string; anomaly_score: number; severity: string; top_factor: string; }
interface Props { anomalies: AnomalyInfo[]; totalAnomalies: number; appName: string; }

const sevColor: Record<string, string> = { low: "text-gray-400", medium: "text-yellow-600 dark:text-yellow-400", high: "text-orange-600 dark:text-orange-400", critical: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScoreCard({ anomalies, totalAnomalies, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Anomaly Scores</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {totalAnomalies > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">{totalAnomalies} detected</span>}
      </div>
      {anomalies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No anomalies</p>
      ) : (
        <div className="space-y-1">
          {anomalies.map((a) => (
            <div key={a.request_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.consumer_id}</span>
              <span className={sevColor[a.severity]}>{(a.anomaly_score * 100).toFixed(0)}% · {a.top_factor}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
