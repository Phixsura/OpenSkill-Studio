"use client";

interface LeaderboardEntry { rank: number; name: string; value: number; compositeScore: number; }
interface MyRank { rank: number; total: number; percentile: number; score: number; }

export function DeveloperLeaderboardPanel({
  entries, myRank, metric,
}: {
  entries: LeaderboardEntry[]; myRank: MyRank | null; metric: string;
}) {
  const medals = ["🥇", "🥈", "🥉"];
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🏆 Developer Leaderboard</h2>
      {myRank && (
        <div className="rounded-xl bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 p-3 text-center">
          <span className="text-xs text-gray-500">Your Rank</span>
          <span className="text-2xl font-bold block">#{myRank.rank}</span>
          <span className="text-xs text-gray-500">Top {myRank.percentile}% · Score: {myRank.score}</span>
        </div>
      )}
      <div className="space-y-0.5">
        {entries.map((e) => (
          <div key={e.rank} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-6 text-center">{e.rank <= 3 ? medals[e.rank - 1] : `#${e.rank}`}</span>
              <span className="font-semibold text-sm">{e.name}</span>
            </div>
            <span className="font-bold text-sm">{typeof e.value === "number" ? e.value.toLocaleString() : e.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
