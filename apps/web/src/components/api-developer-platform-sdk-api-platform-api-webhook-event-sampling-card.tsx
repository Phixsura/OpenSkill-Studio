"use client";

interface SampleInfo { event_id: string; event_type: string; status_code: number; latency_ms: number; }
interface Props { samples: SampleInfo[]; totalCount: number; errorCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformApiWebhookEventSamplingCard({ samples, totalCount, errorCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔬 Event Sampling</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalCount} sampled</p>
        </div>
        {errorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{errorCount} errors</span>}
      </div>
      {samples.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sampled events</p>
      ) : (
        <div className="space-y-1">
          {samples.slice(0, 6).map((s) => (
            <div key={s.event_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.event_type}</span>
              <span className={`font-mono ${s.status_code >= 400 ? "text-red-500" : "text-gray-400"}`}>{s.status_code} · {s.latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
