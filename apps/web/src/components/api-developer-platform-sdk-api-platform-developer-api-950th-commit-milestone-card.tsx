"use client";

interface Stats { total_commits: number; total_pairs: number; backend_tests: number; frontend_tests: number; security_fixes: number; }
interface Props { stats: Stats; currentMilestone: string; nextMilestone: number; progressPct: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApi950thCommitMilestoneCard({ stats, currentMilestone, nextMilestone, progressPct, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-purple-400 bg-gradient-to-br from-purple-50 to-indigo-50 p-5 shadow-lg dark:border-purple-600 dark:from-gray-900 dark:to-gray-800">
      <div className="mb-4 text-center">
        <h3 className="text-lg font-black text-purple-600 dark:text-purple-400">🌟 {currentMilestone}</h3>
        <p className="text-xs text-gray-500">{appName} — commit #{stats.total_commits}</p>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="text-xl font-black text-gray-900 dark:text-gray-100">{stats.total_pairs}</div><div className="text-gray-400">Pairs</div></div>
        <div><div className="text-xl font-black text-gray-900 dark:text-gray-100">{stats.total_commits}</div><div className="text-gray-400">Commits</div></div>
      </div>
      <div className="mb-2">
        <div className="flex justify-between text-[10px] text-gray-400"><span>{stats.total_commits}</span><span>{nextMilestone}</span></div>
        <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500" style={{ width: `${progressPct}%` }} />
        </div>
      </div>
      <p className="text-center text-[10px] text-gray-400">🛡️ {stats.security_fixes} security fixes · {stats.backend_tests + stats.frontend_tests} total tests</p>
    </div>
  );
}
