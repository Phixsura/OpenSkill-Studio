"use client";

interface OverviewInfo {
    total_services: number; total_consumers: number; total_api_calls_today: number;
    platform_health: string; health_emoji: string; uptime_pct: number; avg_latency_ms: number; error_rate_pct: number;
    webhook_success_rate: number; active_destinations: number; queue_depth: number;
    security_score: number; active_api_keys: number;
    nps: number; active_developers: number; support_tickets_open: number;
    consumer_growth_pct: number; revenue_mrr_cents: number; overall_score: number;
}
interface Props { overview: OverviewInfo; appName: string; }

function fmtCents(c: number) { return `$${(c / 100).toFixed(0)}`; }

export default function APIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboardCard({ overview: o, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-indigo-300 bg-gradient-to-br from-indigo-50 via-white to-green-50 p-6 shadow-2xl dark:border-indigo-700 dark:from-gray-900 dark:via-gray-800 dark:to-green-900">
            <div className="mb-4 text-center">
                <h3 className="text-lg font-black text-gray-900 dark:text-gray-100">{o.health_emoji} Platform Overview</h3>
                <p className="text-xs text-gray-500">{appName} · {o.total_services} services</p>
                <span className="mt-1 inline-block text-3xl font-black text-indigo-600">{o.overall_score}</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5 text-center">
                {[
                    { l: "Uptime", v: `${o.uptime_pct}%` },
                    { l: "Latency", v: `${o.avg_latency_ms}ms` },
                    { l: "Errors", v: `${o.error_rate_pct}%` },
                    { l: "Webhooks", v: `${o.webhook_success_rate}%` },
                    { l: "Queue", v: o.queue_depth },
                    { l: "Security", v: o.security_score },
                    { l: "NPS", v: o.nps },
                    { l: "Developers", v: o.active_developers },
                    { l: "Consumers", v: o.total_consumers.toLocaleString() },
                    { l: "API Calls", v: o.total_api_calls_today.toLocaleString() },
                    { l: "MRR", v: fmtCents(o.revenue_mrr_cents) },
                    { l: "Growth", v: `${o.consumer_growth_pct > 0 ? "+" : ""}${o.consumer_growth_pct}%` },
                ].map((m) => (
                    <div key={m.l} className="rounded bg-white/80 py-1 dark:bg-gray-800/80">
                        <p className="text-[10px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
                        <p className="text-[7px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
