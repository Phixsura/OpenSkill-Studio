"use client";

interface CelebrationInfo {
    milestone: number; total_backend: number; total_frontend: number; total_components: number;
    sessions_contributing: number; security_fixes: number; test_suites: number; all_passing: boolean;
    achievement: string;
}
interface Props { celebration: CelebrationInfo; appName: string; }

export default function APIDeveloperPlatformSDK800thCommitCelebrationCard({ celebration: c, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-amber-400 bg-gradient-to-br from-amber-50 via-white to-purple-50 p-6 shadow-2xl dark:border-amber-600 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
            <div className="mb-4 text-center">
                <p className="text-4xl">🏆🎉✨</p>
                <h3 className="text-xl font-black text-gray-900 dark:text-gray-100">{c.milestone} COMMITS</h3>
                <p className="text-xs text-gray-500">{appName} — Developer Platform SDK</p>
                <p className="mt-2 text-lg font-black text-amber-600">{c.achievement}</p>
            </div>
            <div className="grid grid-cols-4 gap-2 text-center">
                {[
                    { l: "Backend", v: c.total_backend },
                    { l: "Frontend", v: c.total_frontend },
                    { l: "Components", v: c.total_components },
                    { l: "Tests", v: c.test_suites },
                    { l: "Sessions", v: c.sessions_contributing },
                    { l: "Security", v: c.security_fixes },
                    { l: "Milestone", v: c.milestone },
                    { l: "Status", v: c.all_passing ? "✅" : "❌" },
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
