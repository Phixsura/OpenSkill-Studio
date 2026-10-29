"use client";

interface MilestoneInfo { total_backend: number; total_frontend: number; total_components: number; total_commits: number; sessions: number; all_passing: boolean; achievement: string; }
interface Props { milestone: MilestoneInfo; appName: string; }

export default function APIDeveloperPlatformSDK860thCommitMilestoneCard({ milestone: m, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-yellow-400 bg-gradient-to-br from-yellow-50 via-white to-red-50 p-6 shadow-2xl dark:border-yellow-600 dark:from-gray-900 dark:via-gray-800 dark:to-red-900">
            <div className="mb-4 text-center">
                <p className="text-4xl">🏆🎉🔥✨🚀</p>
                <h3 className="text-2xl font-black text-gray-900 dark:text-gray-100">{m.total_commits} COMMITS</h3>
                <p className="text-xs text-gray-500">{appName}</p>
                <p className="mt-2 text-xl font-black text-yellow-600">{m.achievement}</p>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center">
                {[
                    { l: "Backend", v: m.total_backend },
                    { l: "Frontend", v: m.total_frontend },
                    { l: "Components", v: m.total_components },
                    { l: "Sessions", v: m.sessions },
                ].map((s) => (
                    <div key={s.l} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
                        <p className="text-xl font-black text-yellow-600">{s.v}</p>
                        <p className="text-[8px] text-gray-400">{s.l}</p>
                    </div>
                ))}
            </div>
            <div className="mt-3 text-center">
                <span className="rounded-full bg-green-100 px-3 py-1 text-[11px] font-bold text-green-700">{m.all_passing ? "✅ ALL TESTS PASSING" : "❌"}</span>
            </div>
        </div>
    );
}
