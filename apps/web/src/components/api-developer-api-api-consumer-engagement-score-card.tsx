"use client";

interface ScoreInfo { consumer_id: string; score: number; tier: string; api_call_frequency: number; endpoint_diversity: number; }
interface Props { scores: ScoreInfo[]; tierBreakdown: Record<string, number>; appName: string; }

const tColor: Record<string, string> = { champion: "text-purple-600", active: "text-green-600", moderate: "text-blue-600", casual: "text-yellow-600", dormant: "text-gray-400" };

export default function APIDeveloperAPIApiConsumerEngagementScoreCard({ scores, tierBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏆 Engagement Scores</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {scores.length} consumers</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        {Object.entries(tierBreakdown).map(([tier, count]) => (
          <span key={tier} className={`text-[10px] font-medium ${tColor[tier] ?? ""}`}>{tier}: {count}</span>
        ))}
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No engagement data</p>
      ) : (
        <div className="space-y-1">
          {scores.slice(0, 5).map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className={`font-bold ${tColor[s.tier] ?? ""}`}>{s.score} · {s.tier}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
