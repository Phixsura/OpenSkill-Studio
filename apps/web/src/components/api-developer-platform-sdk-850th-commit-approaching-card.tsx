"use client";

interface ProgressInfo { total_backend: number; total_frontend: number; total_commits: number; total_components: number; sessions: number; security_fixes: number; all_tests_passing: boolean; achievement: string; avg_per_session: number; }
interface Props { progress: ProgressInfo; appName: string; }

export default function APIDeveloperPlatformSDK850thCommitApproachingCard({ progress: p, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-emerald-400 bg-gradient-to-br from-emerald-50 via-white to-indigo-50 p-6 shadow-2xl dark:border-emerald-600 dark:from-gray-900 dark:via-gray-800 dark:to-indigo-900">
            <div className="mb-4 text-center">
                <p className="text-3xl">🏆🚀✨</p>
                <h3 className="text-lg font-black text-gray-900 dark:text-gray-100">Developer Platform SDK</h3>
                <p className="text-xs text-gray-500">{appName}</p>
                <p className="mt-2 text-lg font-black text-emerald-600">{p.achievement}</p>
                <p className="text-[10px] text-gray-400">{p.avg_per_session} components/session</p>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center">
                {[
                    { l: "Backend", v: p.total_backend },
                    { l: "Frontend", v: p.total_frontend },
                    { l: "Components", v: p.total_components },
                    { l: "Commits", v: p.total_commits },
                    { l: "Sessions", v: p.sessions },
                    { l: "Security", v: p.security_fixes },
                    { l: "Per Session", v: p.avg_per_session },
                    { l: "Status", v: p.all_tests_passing ? "✅" : "❌" },
                ].map((m) => (
                    <div key={m.l} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
                        <p className="text-lg font-black text-emerald-600">{m.v}</p>
                        <p className="text-[7px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
