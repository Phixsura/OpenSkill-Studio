"use client";

interface Stats { total_commits: number; total_pairs: number; backend_tests: number; frontend_tests: number; security_fixes: number; total_files: number; }
interface Tier { name: string; emoji: string; unlocked: boolean; }
interface Props { stats: Stats; tiers: Tier[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApi1000thCommitEternalThousandCard({ stats, tiers, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-yellow-500 bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 p-6 shadow-xl dark:border-yellow-600 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="mb-6 text-center">
        <div className="text-4xl">👑</div>
        <h3 className="bg-gradient-to-r from-yellow-600 via-amber-500 to-orange-500 bg-clip-text text-2xl font-black text-transparent">THE ETERNAL THOUSAND</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Commit #{stats.total_commits}</p>
      </div>
      <div className="mb-4 grid grid-cols-3 gap-3 text-center text-[11px]">
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_commits.toLocaleString()}</div><div className="text-gray-400">Commits</div></div>
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_pairs}</div><div className="text-gray-400">Pairs</div></div>
        <div><div className="text-2xl font-black text-gray-900 dark:text-gray-100">{stats.total_files.toLocaleString()}</div><div className="text-gray-400">Files</div></div>
      </div>
      <div className="mb-4 grid grid-cols-3 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.backend_tests.toLocaleString()}</div><div className="text-gray-400">BE Tests</div></div>
        <div><div className="font-semibold text-blue-600 dark:text-blue-400">{stats.frontend_tests.toLocaleString()}</div><div className="text-gray-400">FE Tests</div></div>
        <div><div className="font-semibold text-purple-600 dark:text-purple-400">{stats.security_fixes}</div><div className="text-gray-400">Security</div></div>
      </div>
      <div className="space-y-0.5">
        {tiers.map((t) => (
          <div key={t.name} className="flex items-center gap-1.5 text-[10px]">
            <span>{t.emoji}</span>
            <span className={t.unlocked ? "font-medium text-gray-700 dark:text-gray-300" : "text-gray-400"}>{t.name}</span>
            {t.unlocked && <span className="text-green-500">✓</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
