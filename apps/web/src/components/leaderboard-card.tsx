"use client";

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  score: number;
}

interface LeaderboardCardProps {
  entries: LeaderboardEntry[];
  boardName: string;
  appName: string;
  totalPlayers: number;
}

const MEDAL: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

function formatScore(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  if (n % 1 !== 0) return n.toFixed(1);
  return n.toString();
}

export default function LeaderboardCard({
  entries,
  boardName,
  appName,
  totalPlayers,
}: LeaderboardCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{boardName}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalPlayers} players</span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scores yet</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div
              key={e.rank}
              className={`flex items-center justify-between rounded px-3 py-2 ${
                e.rank <= 3
                  ? "bg-yellow-50/50 dark:bg-yellow-900/10"
                  : "hover:bg-gray-50 dark:hover:bg-gray-800/50"
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="w-8 text-center text-sm font-bold text-gray-500">
                  {MEDAL[e.rank] ?? `#${e.rank}`}
                </span>
                <span className="text-sm text-gray-800 dark:text-gray-200">{e.user_id}</span>
              </div>
              <span className="font-mono text-sm font-medium text-gray-700 dark:text-gray-300">
                {formatScore(e.score)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
