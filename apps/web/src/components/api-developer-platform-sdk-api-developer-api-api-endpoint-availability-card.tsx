"use client";

interface EndpointInfo { endpoint: string; availability_pct: number; nines: string; current_status: string; }
interface Props { endpoints: EndpointInfo[]; overallAvailability: number; belowTargetCount: number; appName: string; }

const sDot: Record<string, string> = { up: "bg-green-500", down: "bg-red-500", degraded: "bg-yellow-500" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiEndpointAvailabilityCard({ endpoints, overallAvailability, belowTargetCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Availability</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {overallAvailability}%</p>
        </div>
        {belowTargetCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{belowTargetCount} below SLA</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No availability data</p>
      ) : (
        <div className="space-y-1">
          {endpoints.map((e) => (
            <div key={e.endpoint} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[e.current_status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{e.endpoint}</span>
              </div>
              <span className="text-gray-400">{e.availability_pct}% ({e.nines})</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
