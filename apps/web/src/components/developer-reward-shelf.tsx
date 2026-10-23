"use client";

interface Reward { id: string; name: string; icon: string; xp: number; }
interface DeveloperRewardShelfProps { earned: Reward[]; totalXp: number; level: number;
  xpToNext: number; nextLevelXp: number; }

export function DeveloperRewardShelf({ earned, totalXp, level, xpToNext, nextLevelXp }: DeveloperRewardShelfProps) {
  const progressPct = Math.round(((nextLevelXp - xpToNext) / Math.max(nextLevelXp, 1)) * 100);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Rewards</h2>
        <div className="text-right">
          <span className="text-xl font-bold">Level {level}</span>
          <p className="text-xs text-gray-400">{totalXp} XP</p>
        </div>
      </div>
      <div>
        <div className="flex justify-between text-xs text-gray-400">
          <span>Level {level}</span>
          <span>{xpToNext} XP to Level {level + 1}</span>
        </div>
        <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-full rounded-full bg-purple-500" style={{ width: `${progressPct}%` }} />
        </div>
      </div>
      <div className="flex flex-wrap gap-3">
        {earned.map(r => (
          <div key={r.id} className="flex flex-col items-center rounded-lg border p-3 dark:border-gray-700" title={r.name}>
            <span className="text-2xl">{r.icon}</span>
            <p className="mt-1 text-xs font-medium">{r.name}</p>
            <p className="text-[10px] text-purple-500">+{r.xp} XP</p>
          </div>
        ))}
        {earned.length === 0 && <p className="text-sm text-gray-400">No rewards yet — keep building!</p>}
      </div>
    </div>
  );
}
