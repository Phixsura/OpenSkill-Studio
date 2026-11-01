"use client";

interface DashInfo {
    total_requests_24h: number; total_requests_7d: number; total_requests_30d: number;
    unique_consumers_24h: number; unique_endpoints: number;
    avg_latency_ms: number; p99_latency_ms: number; error_rate_pct: number;
    top_endpoint: string; top_consumer: string;
    webhook_deliveries_24h: number; cache_hit_rate_pct: number;
    daily_growth_pct: number; health: string;
}
interface Props { dashboard: DashInfo; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboardCard({ dashboard: d, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-indigo-200 bg-white p-6 shadow-lg dark:border-indigo-800 dark:bg-gray-900">
            <div className="mb-4 flex items-center justify-between">
                <div>
                    <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">📊 API Usage Dashboard</h3>
                    <p className="text-xs text-gray-500">{appName}</p>
                </div>
                <span className={`text-sm font-black ${hColor[d.health] ?? ""}`}>{d.health.toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5 text-center">
                {[
                    { l: "24h Requests", v: d.total_requests_24h.toLocaleString() },
                    { l: "7d Requests", v: d.total_requests_7d.toLocaleString() },
                    { l: "Consumers", v: d.unique_consumers_24h },
                    { l: "Endpoints", v: d.unique_endpoints },
                    { l: "Avg ms", v: d.avg_latency_ms },
                    { l: "p99 ms", v: d.p99_latency_ms },
                    { l: "Errors", v: `${d.error_rate_pct}%` },
                    { l: "Growth", v: `${d.daily_growth_pct > 0 ? "+" : ""}${d.daily_growth_pct}%` },
                    { l: "Webhooks", v: d.webhook_deliveries_24h.toLocaleString() },
                    { l: "Cache Hit", v: `${d.cache_hit_rate_pct}%` },
                    { l: "Top EP", v: d.top_endpoint || "—" },
                    { l: "Top Consumer", v: d.top_consumer || "—" },
                ].map((m) => (
                    <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
                        <p className="text-[10px] font-bold text-gray-900 dark:text-gray-100 truncate px-1">{m.v}</p>
                        <p className="text-[7px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
