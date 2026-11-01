"use client";

interface ServiceUptimeInfo {
  service_id: string;
  is_up: boolean;
  uptime_pct: number;
  downtime_count: number;
  last_downtime_reason: string;
}

interface UptimeMonitorCardProps {
  services: ServiceUptimeInfo[];
  appName: string;
}

export default function UptimeMonitorCard({ services, appName }: UptimeMonitorCardProps) {
  const downCount = services.filter((s) => !s.is_up).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Uptime Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {downCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {downCount} down
          </span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            All up
          </span>
        )}
      </div>

      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services monitored</p>
      ) : (
        <div className="space-y-2">
          {services.map((s) => {
            const uptimeColor =
              s.uptime_pct >= 99.9
                ? "text-green-600 dark:text-green-400"
                : s.uptime_pct >= 99
                  ? "text-yellow-600"
                  : "text-red-600 dark:text-red-400";
            return (
              <div
                key={s.service_id}
                className={`flex items-center justify-between rounded-lg border px-3 py-2 ${
                  s.is_up
                    ? "border-gray-100 dark:border-gray-800"
                    : "border-red-200 bg-red-50/50 dark:border-red-900/50 dark:bg-red-950/10"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${s.is_up ? "bg-green-500" : "animate-pulse bg-red-500"}`}
                  />
                  <div>
                    <span className="text-sm text-gray-800 dark:text-gray-200">{s.service_id}</span>
                    {!s.is_up && s.last_downtime_reason && (
                      <p className="text-[10px] text-red-500">{s.last_downtime_reason}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className={`font-medium ${uptimeColor}`}>{s.uptime_pct}%</span>
                  {s.downtime_count > 0 && (
                    <span className="text-gray-400">{s.downtime_count} outages</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
