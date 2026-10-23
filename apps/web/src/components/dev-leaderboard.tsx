"use client";

interface LeaderboardEntry { name: string; rank: number; badge: string;
  score: number; commits: number; pullRequests: number; reviews: number; deploys: number; }
interface DevLeaderboardProps { leaderboard: LeaderboardEntry[]; period: string; }

export function DevLeaderboard({ leaderboard, period }: DevLeaderboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏆 Developer Leaderboard</h3>
        <span className="text-xs text-gray-400 capitalize">{period}</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 w-10">#</th><th className="p-3 text-left">Developer</th>
          <th className="p-3">Commits</th><th className="p-3">PRs</th>
          <th className="p-3">Reviews</th><th className="p-3">Deploys</th>
          <th className="p-3">Score</th>
        </tr></thead>
        <tbody>
          {leaderboard.map(d => (
            <tr key={d.name} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 text-center">{d.badge || d.rank}</td>
              <td className="p-3 font-medium">{d.name}</td>
              <td className="p-3 text-center">{d.commits}</td>
              <td className="p-3 text-center">{d.pullRequests}</td>
              <td className="p-3 text-center">{d.reviews}</td>
              <td className="p-3 text-center">{d.deploys}</td>
              <td className="p-3 text-center font-bold">{d.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
