"use client";

interface DevEntry { rank: number; name: string; appCount: number; totalInstalls: number; score: number; }
interface DeveloperLeaderboardProps { entries: DevEntry[]; }

export function DeveloperLeaderboard({ entries }: DeveloperLeaderboardProps) {
  if (entries.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No developers</p>;
  return (
    <div className="space-y-2">
      {entries.map(e => (
        <div key={e.rank} className="flex items-center gap-3 rounded border border-gray-200 p-3 dark:border-gray-700">
          <span className="w-8 text-center text-lg font-bold text-gray-400">#{e.rank}</span>
          <div className="flex-1"><span className="font-semibold">{e.name}</span>
            <span className="ml-2 text-xs text-gray-500">{e.appCount} apps · {e.totalInstalls} installs</span></div>
          <span className="font-mono text-sm font-bold text-blue-600">{e.score}</span>
        </div>
      ))}
    </div>
  );
}
