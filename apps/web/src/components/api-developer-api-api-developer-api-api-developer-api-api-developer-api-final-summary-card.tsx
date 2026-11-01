"use client";

interface SummaryInfo {
    total_backend_services: number; total_frontend_components: number;
    total_commits: number; total_security_fixes: number; total_test_suites: number;
    dimension_count: number; verdict: string; all_tests_passing: boolean;
}
interface Props { summary: SummaryInfo; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiFinalSummaryCard({ summary: s, appName }: Props) {
    return (
        <div className="rounded-xl border-4 border-purple-400 bg-gradient-to-br from-purple-50 via-white to-yellow-50 p-6 shadow-2xl dark:border-purple-600 dark:from-gray-900 dark:via-gray-800 dark:to-yellow-900">
            <div className="mb-4 text-center">
                <p className="text-3xl">🏆✨🎉</p>
                <h3 className="text-lg font-black text-gray-900 dark:text-gray-100">Developer Platform SDK</h3>
                <p className="text-xs text-gray-500">{appName}</p>
                <p className="mt-2 text-xl font-black text-purple-600">{s.verdict}</p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
                {[
                    { l: "Backend", v: s.total_backend_services },
                    { l: "Frontend", v: s.total_frontend_components },
                    { l: "Commits", v: s.total_commits },
                    { l: "Tests", v: s.total_test_suites },
                    { l: "Security", v: s.total_security_fixes },
                    { l: "Dimensions", v: s.dimension_count },
                ].map((m) => (
                    <div key={m.l} className="rounded-lg bg-white/80 py-2 shadow-sm dark:bg-gray-800/80">
                        <p className="text-lg font-black text-purple-600">{m.v}</p>
                        <p className="text-[8px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
            <div className="mt-3 text-center">
                <span className={`rounded-full px-3 py-1 text-[11px] font-bold ${s.all_tests_passing ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {s.all_tests_passing ? "✅ ALL TESTS PASSING" : "❌ TESTS FAILING"}
                </span>
            </div>
        </div>
    );
}
