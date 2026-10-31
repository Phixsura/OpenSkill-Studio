"use client";

interface ScoreInfo { consumer_id: string; score: number; tier: string; violations: number; }
interface Props { scores: ScoreInfo[]; blockedCount: number; appName: string; }

const tierColor: Record<string, string> = { trusted: "text-green-600 dark:text-green-400", standard: "text-blue-600 dark:text-blue-400", restricted: "text-orange-600 dark:text-orange-400", blocked: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputationCard({ scores, blockedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⭐ Consumer Reputation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {blockedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🚫 {blockedCount} blocked</span>}
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No reputation data</p>
      ) : (
        <div className="space-y-1">
          {scores.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className={tierColor[s.tier] ?? "text-gray-400"}>{s.score} · {s.tier}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
