"use client";

interface PredictionInfo { consumer_id: string; churn_risk_score: number; risk_level: string; days_since_last_call: number; api_calls_trend_pct: number; }
interface Props { predictions: PredictionInfo[]; atRiskCount: number; appName: string; }

const rColor: Record<string, string> = { critical: "text-red-600 font-bold", high: "text-orange-600", medium: "text-yellow-600", low: "text-green-600" };

export default function APIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictorCard({ predictions, atRiskCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Churn Predictor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {atRiskCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{atRiskCount} at risk</span>}
      </div>
      {predictions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No churn predictions</p>
      ) : (
        <div className="space-y-1">
          {predictions.slice(0, 5).map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <div className="flex gap-2 text-[10px]">
                <span className={rColor[p.risk_level] ?? ""}>{p.churn_risk_score} · {p.risk_level}</span>
                <span className="text-gray-400">{p.days_since_last_call}d idle</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
