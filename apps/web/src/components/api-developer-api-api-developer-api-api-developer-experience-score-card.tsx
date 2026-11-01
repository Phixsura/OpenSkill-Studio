"use client";

interface DXInfo {
    doc_coverage_pct: number; onboarding_completion_pct: number;
    uptime_pct: number; avg_latency_ms: number; nps: number;
    avg_ticket_resolution_hours: number; active_developers: number;
    dx_score: number; dx_grade: string;
}
interface Props { dx: DXInfo; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScoreCard({ dx, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-blue-200 bg-white p-5 shadow-lg dark:border-blue-800 dark:bg-gray-900">
            <div className="mb-4 flex items-center justify-between">
                <div>
                    <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">✨ Developer Experience</h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
                </div>
                <div className="text-center">
                    <span className={`text-3xl font-black ${gColor[dx.dx_grade] ?? ""}`}>{dx.dx_grade}</span>
                    <p className="text-[9px] text-gray-400">{dx.dx_score}/100</p>
                </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
                {[
                    { l: "Docs", v: `${dx.doc_coverage_pct}%` },
                    { l: "Onboarding", v: `${dx.onboarding_completion_pct}%` },
                    { l: "Uptime", v: `${dx.uptime_pct}%` },
                    { l: "Latency", v: `${dx.avg_latency_ms}ms` },
                    { l: "NPS", v: dx.nps },
                    { l: "Developers", v: dx.active_developers },
                ].map((m) => (
                    <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
                        <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
                        <p className="text-[8px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
