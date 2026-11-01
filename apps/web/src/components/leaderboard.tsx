"use client";

interface LeaderboardEntry { rank: number; name: string; icon: string; value: number; author: string; medal: string; }
interface LeaderboardProps { entries: LeaderboardEntry[]; metric: string; period: string; }

export function Leaderboard({ entries, metric, period }: LeaderboardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">🏆 Top Apps</h3>
        <span className="text-xs text-gray-400 capitalize">{metric} · {period.replace("_", " ")}</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {entries.map(e => (
          <div key={e.rank} className="flex items-center gap-3 px-4 py-2.5">
            <span className="w-6 text-center font-bold text-sm">{e.medal || `#${e.rank}`}</span>
            <span className="text-lg">{e.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{e.name}</p>
              <p className="text-xs text-gray-400">by {e.author}</p>
            </div>
            <span className="text-sm font-bold">{e.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
