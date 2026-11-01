"use client";

interface DeveloperRewardsPanelProps { level: string; icon: string; totalPoints: number; nextLevel?: { name: string; points_needed: number } | null; badges: string[]; }

export function DeveloperRewardsPanel({ level, icon, totalPoints, nextLevel, badges }: DeveloperRewardsPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{icon}</span>
        <div>
          <h3 className="font-semibold">{level}</h3>
          <p className="text-sm text-gray-500">{totalPoints.toLocaleString()} points</p>
        </div>
      </div>
      {nextLevel && (
        <div className="mt-3">
          <div className="flex justify-between text-xs">
            <span>{level}</span><span>{nextLevel.name}</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-full rounded-full bg-purple-500" style={{ width: `${Math.max(5, 100 - (nextLevel.points_needed / 3))}%` }} />
          </div>
          <p className="mt-1 text-xs text-gray-400">{nextLevel.points_needed} points to {nextLevel.name}</p>
        </div>
      )}
      {badges.length > 0 && (
        <div className="mt-3 flex gap-1">{badges.map((b, i) => <span key={i} className="text-lg">{b}</span>)}</div>
      )}
    </div>
  );
}
