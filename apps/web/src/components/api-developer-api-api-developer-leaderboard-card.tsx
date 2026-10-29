"use client";

interface EntryInfo { developer_id: string; display_name: string; total_score: number; rank_tier: string; }
interface Props { entries: EntryInfo[]; tierCounts: Record<string, number>; appName: string; }

const tierEmoji: Record<string, string> = { diamond: "💎", platinum: "🏆", gold: "🥇", silver: "🥈", bronze: "🥉" };
const tierColor: Record<string, string> = { diamond: "text-cyan-500", platinum: "text-purple-600", gold: "text-yellow-500", silver: "text-gray-400", bronze: "text-orange-600" };

export default function APIDeveloperAPIApiDeveloperLeaderboardCard({ entries, tierCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 Developer Leaderboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(tierCounts).map(([tier, count]) => (
          <span key={tier} className={`text-[10px] ${tierColor[tier] ?? ""}`}>{tierEmoji[tier] ?? ""} {count}</span>
        ))}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No developers</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e, i) => (
            <div key={e.developer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="text-gray-400 font-mono w-4">#{i + 1}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.display_name}</span>
              </div>
              <span className={`font-bold ${tierColor[e.rank_tier] ?? ""}`}>{e.total_score} {tierEmoji[e.rank_tier] ?? ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
