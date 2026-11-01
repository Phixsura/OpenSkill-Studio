"use client";

interface Stats { total_pairs: number; total_commits: number; backend_tests: number; frontend_tests: number; security_fixes: number; }
interface Props { stats: Stats; tier: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApi800thPairMilestoneCard({ stats, tier, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-emerald-400 bg-gradient-to-br from-emerald-50 to-teal-50 p-6 shadow-xl dark:border-emerald-600 dark:from-gray-900 dark:to-gray-800">
      <div className="mb-4 text-center">
        <div className="text-4xl">🏆🏆</div>
        <h3 className="bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-2xl font-black text-transparent">{tier}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Pair #{stats.total_pairs}</p>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="text-xl font-black text-gray-900 dark:text-gray-100">{stats.total_pairs}</div><div className="text-gray-400">Pairs</div></div>
        <div><div className="text-xl font-black text-gray-900 dark:text-gray-100">{stats.total_commits.toLocaleString()}</div><div className="text-gray-400">Commits</div></div>
        <div><div className="font-semibold text-green-600">{stats.backend_tests.toLocaleString()}</div><div className="text-gray-400">BE Tests</div></div>
        <div><div className="font-semibold text-blue-600">{stats.frontend_tests.toLocaleString()}</div><div className="text-gray-400">FE Tests</div></div>
      </div>
    </div>
  );
}
