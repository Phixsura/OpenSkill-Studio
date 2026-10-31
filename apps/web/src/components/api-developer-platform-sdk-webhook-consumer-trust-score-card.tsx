"use client";

interface ScoreInfo { consumer_id: string; trust_score: number; trust_tier: string; violations: number; days_active: number; }
interface Props { scores: ScoreInfo[]; restrictedCount: number; appName: string; }

const tColor: Record<string, string> = { trusted: "text-green-600", verified: "text-blue-600", standard: "text-yellow-600", restricted: "text-red-600" };

export default function APIDeveloperPlatformSDKWebhookConsumerTrustScoreCard({ scores, restrictedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Trust Scores</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {restrictedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{restrictedCount} restricted</span>}
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No trust data</p>
      ) : (
        <div className="space-y-1">
          {scores.slice(0, 5).map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className={`font-bold ${tColor[s.trust_tier] ?? ""}`}>{s.trust_score} · {s.trust_tier}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
