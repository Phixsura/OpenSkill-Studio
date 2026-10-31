"use client";

interface HealthInfo {
    index: number; grade: string; trend_emoji: string;
    availability_score: number; latency_score: number; error_rate_score: number;
    webhook_score: number; security_score: number; dx_score: number;
}
interface Props { health: HealthInfo; appName: string; }

const gColor: Record<string, string> = { "A+": "text-green-600", A: "text-green-600", "B+": "text-blue-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndexCard({ health: h, appName }: Props) {
    return (
        <div className="rounded-xl border-2 border-green-200 bg-white p-6 shadow-lg dark:border-green-800 dark:bg-gray-900">
            <div className="mb-4 text-center">
                <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">{h.trend_emoji} Platform Health Index</h3>
                <p className="text-xs text-gray-500">{appName}</p>
                <div className="mt-2">
                    <span className={`text-4xl font-black ${gColor[h.grade] ?? ""}`}>{h.grade}</span>
                    <p className="text-sm text-gray-400">{h.index}/100</p>
                </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
                {[
                    { l: "Availability", v: h.availability_score },
                    { l: "Latency", v: h.latency_score },
                    { l: "Error Rate", v: h.error_rate_score },
                    { l: "Webhooks", v: h.webhook_score },
                    { l: "Security", v: h.security_score },
                    { l: "DX", v: h.dx_score },
                ].map((m) => (
                    <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
                        <p className="text-[12px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
                        <p className="text-[8px] text-gray-400">{m.l}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
