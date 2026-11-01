"use client";

interface ProbeInfo { endpoint: string; success_rate: number; consecutive_failures: number; last_status: number | null; last_response_ms: number | null; }
interface Props { probes: ProbeInfo[]; unhealthyCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbeCard({ probes, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🩺 Health Probes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {probes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health probes</p>
      ) : (
        <div className="space-y-1.5">
          {probes.map((p) => (
            <div key={p.endpoint} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${p.consecutive_failures === 0 ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{p.endpoint}</span>
              </div>
              <span className="text-gray-400">{p.success_rate}% · {p.last_response_ms ?? "—"}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
