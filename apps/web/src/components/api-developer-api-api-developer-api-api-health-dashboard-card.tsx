"use client";

interface ServiceInfo { service_name: string; status: string; response_time_ms: number; consecutive_failures: number; error_message: string; }
interface Props { services: ServiceInfo[]; overallStatus: string; appName: string; }

const sDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", unhealthy: "bg-red-500", unknown: "bg-gray-400" };
const oBanner: Record<string, string> = { healthy: "bg-green-50 text-green-700 border-green-200", degraded: "bg-yellow-50 text-yellow-700 border-yellow-200", unhealthy: "bg-red-50 text-red-700 border-red-200", unknown: "bg-gray-50 text-gray-500 border-gray-200" };

export default function APIDeveloperAPIApiDeveloperApiApiHealthDashboardCard({ services, overallStatus, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Health Dashboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className={`mb-3 rounded-lg border px-3 py-1.5 text-center text-[11px] font-bold ${oBanner[overallStatus] ?? ""}`}>
        {overallStatus.toUpperCase()}
      </div>
      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services</p>
      ) : (
        <div className="space-y-1.5">
          {services.map((s) => (
            <div key={s.service_name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[s.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{s.service_name}</span>
              </div>
              <span className="text-gray-400">{s.response_time_ms}ms{s.consecutive_failures > 0 ? ` · ${s.consecutive_failures} fails` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
