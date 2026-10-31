"use client";

interface Tier { id: string; name: string; uptimePct: number; maxLatencyMs: number; maxErrorRatePct: number; supportHours: number; }
interface Compliance { uptimeOk: boolean; latencyOk: boolean; errorRateOk: boolean; }
interface Props { tier: Tier; compliance: Compliance | null; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTierCard({ tier, compliance, consumerId, appName }: Props) {
  const allOk = compliance ? compliance.uptimeOk && compliance.latencyOk && compliance.errorRateOk : null;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 SLA Tier</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className="rounded bg-blue-100 px-2 py-0.5 text-[11px] font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{tier.name}</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{tier.uptimePct}%</div>
          <div className="text-[10px] text-gray-400">Uptime</div>
        </div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{tier.maxLatencyMs}ms</div>
          <div className="text-[10px] text-gray-400">P99 Latency</div>
        </div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{tier.maxErrorRatePct}%</div>
          <div className="text-[10px] text-gray-400">Error Rate</div>
        </div>
      </div>
      {compliance && (
        <div className={`rounded-lg p-2 text-center text-[11px] font-medium ${allOk ? "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400" : "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400"}`}>
          {allOk ? "✅ All SLA targets met" : "⚠️ SLA breach detected"}
        </div>
      )}
    </div>
  );
}
