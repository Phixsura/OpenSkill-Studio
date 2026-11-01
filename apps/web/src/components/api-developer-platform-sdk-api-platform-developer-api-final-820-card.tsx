"use client";

interface StatsInfo { total_commits: number; total_backend: number; total_frontend: number; total_tests: number; security_fixes: number; sessions: number; all_passing: boolean; achievement: string; }
interface Props { stats: StatsInfo; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiFinal820Card({ stats: s, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-amber-400 bg-gradient-to-br from-amber-50 via-white to-green-50 p-6 shadow-2xl dark:border-amber-600 dark:from-gray-900 dark:via-gray-800 dark:to-green-900">
            <div className="mb-4 text-center">
                <p className="text-4xl">🏆🎉🚀</p>
                <h3 className="text-xl font-black text-gray-900 dark:text-gray-100">{s.total_commits} COMMITS</h3>
                <p className="text-xs text-gray-500">{appName}</p>
                <p className="mt-2 text-lg font-black text-amber-600">{s.achievement}</p>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center">
                {[
                    { l: "Backend", v: s.total_backend },
                    { l: "Frontend", v: s.total_frontend },
                    { l: "Tests", v: s.total_tests },
                    { l: "Security", v: s.security_fixes },
                    { l: "Sessions", v: s.sessions },
                    { l: "Commits", v: s.total_commits },
                    { l: "Components", v: s.total_backend + s.total_frontend },
                    { l: "Status", v: s.all_passing ? "✅" : "❌" },
                ].map((m) => (
                    <div key={m.l} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
                        <p className="text-lg font-black text-amber-600">{m.v}</p>
                        <p className="text-[7px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
