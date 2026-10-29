"use client";

interface FinaleInfo {
    total_services: number; total_endpoints: number; total_developers: number; total_api_calls: number;
    platform_grade: string; uptime_pct: number; avg_latency_ms: number; error_rate_pct: number;
    webhook_success_rate_pct: number; total_webhook_deliveries: number;
    security_score: number; compliance_rate_pct: number;
    nps_score: number; documentation_coverage_pct: number;
    request_growth_pct: number; developer_growth_pct: number;
    overall_score: number; verdict: string;
}
interface Props { finale: FinaleInfo; appName: string; }

export default function APIDeveloperAPIApiPlatformGrandFinaleCard({ finale: f, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-purple-300 bg-gradient-to-br from-purple-50 to-blue-50 p-6 shadow-xl dark:border-purple-700 dark:from-gray-900 dark:to-gray-800">
            <div className="mb-4 text-center">
                <h3 className="text-lg font-black text-gray-900 dark:text-gray-100">🎆 Developer Platform SDK</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {f.total_services} services</p>
                <div className="mt-2">
                    <span className="text-4xl font-black text-purple-600">{f.overall_score}</span>
                    <p className="text-sm font-bold">{f.verdict}</p>
                </div>
            </div>
            <div className="grid grid-cols-4 gap-1.5 text-center">
                {[
                    { l: "Uptime", v: `${f.uptime_pct}%` },
                    { l: "Latency", v: `${f.avg_latency_ms}ms` },
                    { l: "Errors", v: `${f.error_rate_pct}%` },
                    { l: "Grade", v: f.platform_grade },
                    { l: "Webhooks", v: `${f.webhook_success_rate_pct}%` },
                    { l: "Security", v: f.security_score },
                    { l: "Compliance", v: `${f.compliance_rate_pct}%` },
                    { l: "NPS", v: f.nps_score },
                    { l: "Developers", v: f.total_developers.toLocaleString() },
                    { l: "API Calls", v: f.total_api_calls.toLocaleString() },
                    { l: "Doc Cover", v: `${f.documentation_coverage_pct}%` },
                    { l: "Growth", v: `${f.request_growth_pct > 0 ? "+" : ""}${f.request_growth_pct}%` },
                ].map((m) => (
                    <div key={m.l} className="rounded bg-white/80 py-1 dark:bg-gray-800/80">
                        <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
                        <p className="text-[7px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
