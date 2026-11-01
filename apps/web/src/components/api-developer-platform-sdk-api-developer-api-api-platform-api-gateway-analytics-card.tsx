"use client";

interface AnalyticsInfo {
    total_requests: number; error_rate_pct: number; avg_latency_ms: number; p99_latency_ms: number;
    cache_hit_rate_pct: number; rate_limited_requests: number; auth_failures: number; health: string;
}
interface Props { analytics: AnalyticsInfo; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalyticsCard({ analytics: a, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-gray-200 bg-white p-5 shadow-lg dark:border-gray-700 dark:bg-gray-900">
            <div className="mb-4 flex items-center justify-between">
                <div>
                    <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">🚪 Gateway Analytics</h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
                </div>
                <span className={`text-sm font-black ${hColor[a.health] ?? ""}`}>{a.health.toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5 text-center">
                {[
                    { l: "Requests", v: a.total_requests.toLocaleString() },
                    { l: "Error Rate", v: `${a.error_rate_pct}%` },
                    { l: "Avg ms", v: a.avg_latency_ms },
                    { l: "p99 ms", v: a.p99_latency_ms },
                    { l: "Cache Hit", v: `${a.cache_hit_rate_pct}%` },
                    { l: "Rate Limited", v: a.rate_limited_requests },
                    { l: "Auth Fails", v: a.auth_failures },
                    { l: "Health", v: a.health },
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
