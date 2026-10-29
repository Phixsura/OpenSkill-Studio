"use client";

interface DestStatusInfo { destination: string; status: string; consecutive_failures: number; }

interface APIWebhookStatusCardProps { destinations: DestStatusInfo[]; appName: string; }

const sColor: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500", unknown: "bg-gray-400" };

export default function APIWebhookStatusCard({ destinations, appName }: APIWebhookStatusCardProps) {
  const unhealthy = destinations.filter((d) => d.status !== "healthy").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🟢 Webhook Status</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{destinations.length} destinations</span>
          {unhealthy > 0 && <p className="text-[10px] text-red-500">{unhealthy} unhealthy</p>}
        </div>
      </div>
      {destinations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No destinations tracked</p>
      ) : (
        <div className="space-y-1">
          {destinations.map((d) => (
            <div key={d.destination} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${sColor[d.status] ?? "bg-gray-400"}`} />
                <span className="truncate max-w-[170px] text-gray-700 dark:text-gray-300">{d.destination}</span>
              </div>
              <span className="text-gray-400">{d.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
