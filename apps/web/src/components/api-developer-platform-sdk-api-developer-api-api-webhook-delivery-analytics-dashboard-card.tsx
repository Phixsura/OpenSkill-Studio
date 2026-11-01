"use client";

interface DashInfo {
    total_deliveries: number; success_rate: number; retry_rate: number;
    avg_latency_ms: number; p99_latency_ms: number; active_destinations: number;
    dead_letters: number; queue_depth: number; health: string;
}
interface Props { dashboard: DashInfo; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiWebhookDeliveryAnalyticsDashboardCard({ dashboard: d, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-blue-200 bg-white p-5 shadow-lg dark:border-blue-800 dark:bg-gray-900">
            <div className="mb-4 flex items-center justify-between">
                <div>
                    <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">📊 Delivery Analytics</h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
                </div>
                <span className={`text-sm font-black ${hColor[d.health] ?? ""}`}>{d.health.toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5 text-center">
                {[
                    { l: "Deliveries", v: d.total_deliveries.toLocaleString() },
                    { l: "Success", v: `${d.success_rate}%` },
                    { l: "Retry", v: `${d.retry_rate}%` },
                    { l: "Avg ms", v: d.avg_latency_ms },
                    { l: "p99 ms", v: d.p99_latency_ms },
                    { l: "Destinations", v: d.active_destinations },
                    { l: "Dead Letters", v: d.dead_letters },
                    { l: "Queue", v: d.queue_depth },
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
