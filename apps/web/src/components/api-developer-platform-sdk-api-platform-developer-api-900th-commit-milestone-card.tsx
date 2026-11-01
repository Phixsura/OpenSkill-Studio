"use client";

interface Achievement { milestone_id: string; title: string; tier: string; celebration_emoji: string; commit_number: number; }
interface Props { commitCount: number; currentTier: string; achievements: Achievement[]; nextMilestone: number | null; appName: string; }

const tierGradient: Record<string, string> = { legendary: "from-yellow-500 to-orange-500", mythic: "from-purple-500 to-pink-500", godlike: "from-blue-500 to-cyan-500", transcendent: "from-emerald-500 to-teal-500", eternal: "from-rose-500 to-red-500" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApi900thCommitMilestoneCard({ commitCount, currentTier, achievements, nextMilestone, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 text-center">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎊 Milestone Tracker</h3>
        <div className={`mt-2 bg-gradient-to-r ${tierGradient[currentTier] ?? "from-gray-400 to-gray-500"} bg-clip-text text-3xl font-black text-transparent`}>{commitCount}</div>
        <p className="text-xs font-bold uppercase tracking-wider text-gray-500">{currentTier}</p>
      </div>
      {achievements.length > 0 && (
        <div className="mb-3 space-y-1">
          {achievements.map((a) => (
            <div key={a.milestone_id} className="flex items-center justify-between text-[11px]">
              <span>{a.celebration_emoji} {a.title}</span>
              <span className="text-gray-400">#{a.commit_number}</span>
            </div>
          ))}
        </div>
      )}
      {nextMilestone && <p className="text-center text-[10px] text-gray-400">Next: {nextMilestone} commits</p>}
    </div>
  );
}
