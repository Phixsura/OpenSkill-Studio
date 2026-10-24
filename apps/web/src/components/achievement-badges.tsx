"use client";

interface Achievement { title: string; icon: string; description: string; points: number; }
interface AchievementBadgesProps { earned: Achievement[]; totalPoints: number;
  level: number; levelTitle: string; nextAt: number | null; }

export function AchievementBadges({ earned, totalPoints, level, levelTitle, nextAt }: AchievementBadgesProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🏅 Achievements</h3>
        <div className="text-right">
          <p className="text-sm font-bold">Level {level}: {levelTitle}</p>
          <p className="text-xs text-gray-400">{totalPoints} points{nextAt ? ` · ${nextAt - totalPoints} to next` : ""}</p>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {earned.map(a => (
          <div key={a.title} className="rounded-lg bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/10 dark:to-orange-900/10 p-3 text-center border border-yellow-200 dark:border-yellow-800">
            <p className="text-2xl mb-1">{a.icon}</p>
            <p className="text-xs font-bold">{a.title}</p>
            <p className="text-[10px] text-gray-400">{a.points}pts</p>
          </div>
        ))}
      </div>
    </div>
  );
}
