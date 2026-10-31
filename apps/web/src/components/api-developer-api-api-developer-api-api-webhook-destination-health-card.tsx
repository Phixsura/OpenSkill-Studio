"use client";

interface HealthInfo { destination: string; success_rate: number; avg_response_ms: number; status: string; total_deliveries: number; consecutive_failures: number; }
interface Props { destinations: HealthInfo[]; unhealthyCount: number; appName: string; }

const sDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", unhealthy: "bg-orange-500", down: "bg-red-500" };

export default function APIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealthCard({ destinations, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Destination Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {destinations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No destinations</p>
      ) : (
        <div className="space-y-1.5">
          {destinations.map((d) => (
            <div key={d.destination} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[d.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{new URL(d.destination).hostname}</span>
              </div>
              <span className="text-gray-400">{d.success_rate}% · {d.avg_response_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
