"use client";

interface ScoreInfo { consumer_id: string; score: number; level: string; }
interface Props { scores: ScoreInfo[]; dormantCount: number; appName: string; }

const levelColor: Record<string, string> = { power_user: "text-purple-600 dark:text-purple-400", active: "text-green-600 dark:text-green-400", moderate: "text-blue-600 dark:text-blue-400", low: "text-yellow-600 dark:text-yellow-400", dormant: "text-gray-400" };
const levelEmoji: Record<string, string> = { power_user: "🔥", active: "✅", moderate: "📊", low: "📉", dormant: "💤" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScoreCard({ scores, dormantCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Engagement Scores</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {dormantCount > 0 && <span className="text-[10px] text-gray-400">💤 {dormantCount} dormant</span>}
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No engagement data</p>
      ) : (
        <div className="space-y-1">
          {scores.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{levelEmoji[s.level]} {s.consumer_id}</span>
              <span className={levelColor[s.level]}>{s.score} · {s.level.replace("_", " ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
