"use client";

interface MilestoneInfo {
    total_backend_services: number; total_frontend_components: number;
    total_test_suites: number; total_commits: number; security_fixes: number;
    milestone_grade: string; coverage_completeness: number;
}
interface Props { milestone: MilestoneInfo; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiPlatformMilestone500Card({ milestone: m, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-yellow-400 bg-gradient-to-br from-yellow-50 via-white to-purple-50 p-6 shadow-2xl dark:border-yellow-600 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
            <div className="mb-4 text-center">
                <p className="text-3xl">🎉🏆🎉</p>
                <h3 className="text-lg font-black text-gray-900 dark:text-gray-100">500 SERVICES MILESTONE</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Developer Platform SDK</p>
                <p className="mt-2 text-xl font-black text-yellow-600">{m.milestone_grade}</p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
                {[
                    { l: "Backend", v: m.total_backend_services },
                    { l: "Frontend", v: m.total_frontend_components },
                    { l: "Test Suites", v: m.total_test_suites },
                    { l: "Commits", v: m.total_commits },
                    { l: "Security Fixes", v: m.security_fixes },
                    { l: "Coverage", v: `${m.coverage_completeness}%` },
                ].map((s) => (
                    <div key={s.l} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
                        <p className="text-lg font-black text-purple-600">{s.v}</p>
                        <p className="text-[8px] text-gray-400">{s.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
