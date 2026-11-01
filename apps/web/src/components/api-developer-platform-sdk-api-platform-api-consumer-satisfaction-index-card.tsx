"use client";

interface IndexInfo { consumer_id: string; csi: number; satisfaction_tier: string; api_reliability_score: number; overall_nps: number; }
interface Props { indices: IndexInfo[]; avgCsi: number; dissatisfiedCount: number; appName: string; }

const tColor: Record<string, string> = { delighted: "text-green-600", satisfied: "text-blue-600", neutral: "text-yellow-600", dissatisfied: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndexCard({ indices, avgCsi, dissatisfiedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">😊 Satisfaction Index</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — avg CSI: {avgCsi}</p>
        </div>
        {dissatisfiedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{dissatisfiedCount} dissatisfied</span>}
      </div>
      {indices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No satisfaction data</p>
      ) : (
        <div className="space-y-1">
          {indices.slice(0, 5).map((i) => (
            <div key={i.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{i.consumer_id}</span>
              <span className={`font-bold ${tColor[i.satisfaction_tier] ?? ""}`}>{i.csi} · {i.satisfaction_tier}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
