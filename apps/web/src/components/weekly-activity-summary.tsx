"use client";

interface Activity { commits: number; deploys: number; reviews_received: number;
  new_installs: number; revenue: number; }
interface WeeklyActivitySummaryProps { developerName: string; week: string; activity: Activity;
  activityScore: number; streakDays: number; topAchievement: string | null; }

export function WeeklyActivitySummary({ developerName, week, activity, activityScore,
  streakDays, topAchievement }: WeeklyActivitySummaryProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Weekly Summary</h2>
          <p className="text-xs text-gray-400">{developerName} · {week}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-black text-blue-600">{activityScore}</p>
          <p className="text-xs text-gray-400">Activity Score</p>
        </div>
      </div>
      {topAchievement && (
        <div className="rounded-lg bg-gradient-to-r from-yellow-50 to-orange-50 p-3 text-center dark:from-yellow-900/10 dark:to-orange-900/10">
          <p className="text-sm font-bold">{topAchievement}</p>
        </div>
      )}
      <div className="grid grid-cols-3 gap-2 text-center sm:grid-cols-5">
        {[
          { label: "Commits", value: activity.commits, icon: "💻" },
          { label: "Deploys", value: activity.deploys, icon: "🚀" },
          { label: "Reviews", value: activity.reviews_received, icon: "⭐" },
          { label: "Installs", value: activity.new_installs, icon: "📥" },
          { label: "Revenue", value: `$${activity.revenue}`, icon: "💰" },
        ].map(s => (
          <div key={s.label} className="rounded bg-gray-50 p-2 dark:bg-gray-800">
            <p className="font-bold">{s.icon} {s.value}</p>
            <p className="text-[10px] text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      {streakDays > 0 && (
        <p className="text-center text-xs text-orange-500">🔥 {streakDays}-day streak</p>
      )}
    </div>
  );
}
