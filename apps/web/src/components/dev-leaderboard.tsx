"use client";

interface Developer { developer: string; rank: number; score: number;
  commits: number; prs: number; reviews: number; }
interface DevLeaderboardProps { leaderboard: Developer[]; totalDevelopers: number; }

const RANK_MEDALS: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

export function DevLeaderboard({ leaderboard, totalDevelopers }: DevLeaderboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏆 Developer Leaderboard</h3>
        <span className="text-xs text-gray-400">{totalDevelopers} developers</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {leaderboard.map(d => (
          <div key={d.developer} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className="w-6 text-center">{RANK_MEDALS[d.rank] ?? `#${d.rank}`}</span>
              <span className="text-sm font-medium">{d.developer}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{d.commits} commits</span>
              <span>{d.prs} PRs</span>
              <span>{d.reviews} reviews</span>
              <span className="font-bold text-blue-600">{d.score} pts</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
