"use client";

interface Instance { id: string; host: string; port: number; healthy: boolean; connections: number; weight: number; }
interface Props { instances: Instance[]; endpointPath: string; strategy: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancerCard({ instances, endpointPath, strategy, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚖️ Load Balancer</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{endpointPath}</code> · {strategy.replace("_", " ")}</p>
      </div>
      {instances.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No backend instances</p>
      ) : (
        <div className="space-y-1">
          {instances.map((i) => (
            <div key={i.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${i.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{i.host}:{i.port}</span>
              </div>
              <span className="text-gray-400">{i.connections} conn · w{i.weight}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
