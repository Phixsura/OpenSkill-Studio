"use client";

interface Stats { total_commits: number; total_pairs: number; total_tests: number; total_files: number; security_fixes: number; }
interface Props { stats: Stats; tier: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApi1100thCommitMilestoneCard({ stats, tier, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-rose-400 bg-gradient-to-br from-rose-50 via-pink-50 to-fuchsia-50 p-6 shadow-xl dark:border-rose-600 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="mb-6 text-center">
        <div className="text-4xl">🌟👑</div>
        <h3 className="bg-gradient-to-r from-rose-600 via-pink-500 to-fuchsia-500 bg-clip-text text-2xl font-black text-transparent">{tier}</h3>
        <p className="text-xs text-gray-500">{appName} — commit #{stats.total_commits}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center text-[11px]">
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_commits.toLocaleString()}</div><div className="text-gray-400">Commits</div></div>
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_pairs}</div><div className="text-gray-400">Pairs</div></div>
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_tests.toLocaleString()}</div><div className="text-gray-400">Tests</div></div>
      </div>
      <p className="mt-4 text-center text-[10px] text-gray-400">🛡️ {stats.security_fixes} security fixes · {stats.total_files.toLocaleString()} files</p>
    </div>
  );
}
