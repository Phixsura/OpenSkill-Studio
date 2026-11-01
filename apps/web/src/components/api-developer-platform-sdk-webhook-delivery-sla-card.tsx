"use client";

interface SLAInfo { destination: string; target_delivery_ms: number; actual_avg_ms: number; target_success_rate_pct: number; actual_success_rate_pct: number; meeting_all_sla: boolean; sla_breaches: number; }
interface Props { slas: SLAInfo[]; breachingCount: number; appName: string; }

export default function APIDeveloperPlatformSDKWebhookDeliverySLACard({ slas, breachingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Delivery SLA</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {breachingCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{breachingCount} breaching</span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">all met</span>
        )}
      </div>
      {slas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery SLAs</p>
      ) : (
        <div className="space-y-2">
          {slas.map((s) => (
            <div key={s.destination} className={`rounded-lg p-2 ${s.meeting_all_sla ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(s.destination).hostname}</span>
                <span className={s.meeting_all_sla ? "text-green-600" : "text-red-500 font-bold"}>{s.meeting_all_sla ? "✓" : "✗"}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>latency: {s.actual_avg_ms}ms / {s.target_delivery_ms}ms</span>
                <span>success: {s.actual_success_rate_pct}% / {s.target_success_rate_pct}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
