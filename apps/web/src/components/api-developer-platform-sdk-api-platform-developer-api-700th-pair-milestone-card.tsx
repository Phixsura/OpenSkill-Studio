"use client";

interface Stats { total_pairs: number; total_commits: number; total_backend_tests: number; total_frontend_tests: number; security_fixes: number; }
interface Props { stats: Stats; milestoneTitle: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApi700thPairMilestoneCard({ stats, milestoneTitle, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-yellow-400 bg-gradient-to-br from-yellow-50 to-amber-50 p-5 shadow-lg dark:border-yellow-600 dark:from-gray-900 dark:to-gray-800">
      <div className="mb-4 text-center">
        <h3 className="text-lg font-black text-yellow-600 dark:text-yellow-400">🏆 {milestoneTitle}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Pair #{stats.total_pairs}</p>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_pairs}</div><div className="text-gray-400">Pairs</div></div>
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_commits}</div><div className="text-gray-400">Commits</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.total_backend_tests}</div><div className="text-gray-400">Backend Tests</div></div>
        <div><div className="font-semibold text-blue-600 dark:text-blue-400">{stats.total_frontend_tests}</div><div className="text-gray-400">Frontend Tests</div></div>
      </div>
      {stats.security_fixes > 0 && <p className="mt-2 text-center text-[10px] text-gray-400">🛡️ {stats.security_fixes} security fixes applied</p>}
    </div>
  );
}
