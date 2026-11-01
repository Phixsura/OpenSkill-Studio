"use client";

interface RateInfo { endpoint: string; current_rps: number; avg_rps: number; peak_rps: number; load_level: string; }
interface Props { rates: RateInfo[]; spikeCount: number; appName: string; }

const lColor: Record<string, string> = { spike: "text-red-600 font-bold", high: "text-orange-600", normal: "text-green-600", low: "text-gray-400" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitorCard({ rates, spikeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Request Rate</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {spikeCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{spikeCount} spikes</span>}
      </div>
      {rates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate data</p>
      ) : (
        <div className="space-y-1">
          {rates.slice(0, 5).map((r) => (
            <div key={r.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              <div className="flex gap-2 text-[10px]">
                <span className={lColor[r.load_level] ?? ""}>{r.current_rps} rps</span>
                <span className="text-gray-400">avg: {r.avg_rps} · peak: {r.peak_rps}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
