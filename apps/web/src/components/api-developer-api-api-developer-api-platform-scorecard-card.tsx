"use client";

interface ScorecardInfo {
    uptime_pct: number; error_rate_pct: number; avg_latency_ms: number; p99_latency_ms: number;
    webhook_delivery_rate_pct: number; dead_letter_count: number;
    security_score: number; compliance_rate_pct: number;
    nps: number; active_developers: number; total_api_calls_30d: number;
    reliability_score: number; performance_score: number; security_grade: string; overall_grade: string;
}
interface Props { scorecard: ScorecardInfo; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };

export default function APIDeveloperAPIApiDeveloperApiPlatformScorecardCard({ scorecard: s, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-green-200 bg-white p-6 shadow-lg dark:border-green-800 dark:bg-gray-900">
            <div className="mb-4 text-center">
                <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">📊 Platform Scorecard</h3>
                <p className="text-xs text-gray-500">{appName}</p>
                <div className="mt-2 flex items-center justify-center gap-4">
                    <div className="text-center">
                        <span className={`text-4xl font-black ${gColor[s.overall_grade] ?? ""}`}>{s.overall_grade}</span>
                        <p className="text-[9px] text-gray-400">Overall</p>
                    </div>
                    <div className="text-center">
                        <span className="text-lg font-bold text-blue-600">{s.reliability_score}</span>
                        <p className="text-[9px] text-gray-400">Reliability</p>
                    </div>
                    <div className="text-center">
                        <span className="text-lg font-bold text-purple-600">{s.performance_score}</span>
                        <p className="text-[9px] text-gray-400">Performance</p>
                    </div>
                    <div className="text-center">
                        <span className={`text-lg font-bold ${gColor[s.security_grade] ?? ""}`}>{s.security_grade}</span>
                        <p className="text-[9px] text-gray-400">Security</p>
                    </div>
                </div>
            </div>
            <div className="grid grid-cols-4 gap-1.5 text-center">
                {[
                    { l: "Uptime", v: `${s.uptime_pct}%` },
                    { l: "Errors", v: `${s.error_rate_pct}%` },
                    { l: "Latency", v: `${s.avg_latency_ms}ms` },
                    { l: "p99", v: `${s.p99_latency_ms}ms` },
                    { l: "Webhooks", v: `${s.webhook_delivery_rate_pct}%` },
                    { l: "Dead Letters", v: s.dead_letter_count },
                    { l: "Compliance", v: `${s.compliance_rate_pct}%` },
                    { l: "NPS", v: s.nps },
                    { l: "Developers", v: s.active_developers.toLocaleString() },
                    { l: "API Calls", v: s.total_api_calls_30d.toLocaleString() },
                    { l: "Security", v: s.security_score },
                    { l: "Grade", v: s.overall_grade },
                ].map((m) => (
                    <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
                        <p className="text-[10px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
                        <p className="text-[7px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
