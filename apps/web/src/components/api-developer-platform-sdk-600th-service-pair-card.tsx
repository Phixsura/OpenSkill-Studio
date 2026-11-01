"use client";

interface MilestoneInfo {
    total_backend: number; total_frontend: number; total_components: number;
    total_commits: number; total_tests: number; sessions: number;
    security_fixes: number; all_passing: boolean; achievement: string;
}
interface Props { milestone: MilestoneInfo; appName: string; }

export default function APIDeveloperPlatformSDK600thServicePairCard({ milestone: m, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-emerald-400 bg-gradient-to-br from-emerald-50 via-white to-amber-50 p-6 shadow-2xl dark:border-emerald-600 dark:from-gray-900 dark:via-gray-800 dark:to-amber-900">
            <div className="mb-4 text-center">
                <p className="text-4xl">🏆🎉🚀✨</p>
                <h3 className="text-2xl font-black text-gray-900 dark:text-gray-100">600 SERVICE PAIRS</h3>
                <p className="text-xs text-gray-500">{appName} — Developer Platform SDK</p>
                <p className="mt-2 text-lg font-black text-emerald-600">{m.achievement}</p>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center">
                {[
                    { l: "Backend", v: m.total_backend },
                    { l: "Frontend", v: m.total_frontend },
                    { l: "Components", v: m.total_components },
                    { l: "Commits", v: m.total_commits },
                    { l: "Tests", v: m.total_tests },
                    { l: "Sessions", v: m.sessions },
                    { l: "Security", v: m.security_fixes },
                    { l: "Status", v: m.all_passing ? "✅ ALL PASS" : "❌" },
                ].map((s) => (
                    <div key={s.l} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
                        <p className="text-lg font-black text-emerald-600">{s.v}</p>
                        <p className="text-[7px] text-gray-400">{s.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
