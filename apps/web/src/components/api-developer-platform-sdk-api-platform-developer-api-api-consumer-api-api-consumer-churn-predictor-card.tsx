"use client";

interface PredictionInfo { consumer_id: string; churn_risk_pct: number; risk_level: string; top_signal: string; }
interface Props { predictions: PredictionInfo[]; atRiskCount: number; appName: string; }

const riskColor: Record<string, string> = { low: "text-green-600 dark:text-green-400", medium: "text-yellow-600 dark:text-yellow-400", high: "text-orange-600 dark:text-orange-400", critical: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictorCard({ predictions, atRiskCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📉 Churn Predictor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {atRiskCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {atRiskCount} at risk</span>}
      </div>
      {predictions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No predictions</p>
      ) : (
        <div className="space-y-1">
          {predictions.map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <span className={riskColor[p.risk_level]}>{p.churn_risk_pct}% · {p.top_signal}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
