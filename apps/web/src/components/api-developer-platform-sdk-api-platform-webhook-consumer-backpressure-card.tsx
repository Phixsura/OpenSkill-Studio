"use client";

interface StateInfo { destination: string; queue_depth: number; processing_rate_per_sec: number; pressure_level: string; estimated_drain_seconds: number; rejection_count: number; }
interface Props { states: StateInfo[]; underPressureCount: number; appName: string; }

const pColor: Record<string, string> = { normal: "text-green-600", moderate: "text-yellow-600", high: "text-orange-600", critical: "text-red-600 font-bold" };

export default function APIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressureCard({ states, underPressureCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Backpressure</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {underPressureCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{underPressureCount} under pressure</span>}
      </div>
      {states.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No backpressure data</p>
      ) : (
        <div className="space-y-1.5">
          {states.map((s) => (
            <div key={s.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{new URL(s.destination).hostname}</span>
              <div className="flex gap-2 text-[10px]">
                <span className={pColor[s.pressure_level] ?? ""}>{s.pressure_level}</span>
                <span className="text-gray-400">{s.queue_depth} queued · drain: {s.estimated_drain_seconds}s</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
