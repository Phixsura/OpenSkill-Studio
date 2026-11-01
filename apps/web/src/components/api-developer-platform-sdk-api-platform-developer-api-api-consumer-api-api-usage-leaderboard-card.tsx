"use client";

interface LeaderboardEntry { rank: number; consumer_id: string; total_requests: number; success_rate: number; score: number; }
interface Props { entries: LeaderboardEntry[]; appName: string; }

const medalEmoji = (rank: number) => rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : `#${rank}`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboardCard({ entries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏆 Usage Leaderboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Top {entries.length}</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="w-5 text-center">{medalEmoji(e.rank)}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.consumer_id}</span>
              </div>
              <span className="text-gray-400">{e.total_requests.toLocaleString()} reqs · {e.success_rate}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
