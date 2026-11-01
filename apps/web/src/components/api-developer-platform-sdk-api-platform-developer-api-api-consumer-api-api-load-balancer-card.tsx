"use client";

interface InstanceInfo { instance_id: string; host: string; healthy: boolean; active_connections: number; }
interface Props { strategy: string; instances: InstanceInfo[]; healthyCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancerCard({ strategy, instances, healthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚖️ Load Balancer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {strategy}</p>
        </div>
        <span className="text-[10px] text-gray-400">{healthyCount}/{instances.length} healthy</span>
      </div>
      <div className="space-y-1">
        {instances.map((i) => (
          <div key={i.instance_id} className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-full ${i.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-gray-700 dark:text-gray-300">{i.host}</span>
            </div>
            <span className="text-gray-400">{i.active_connections} conn</span>
          </div>
        ))}
      </div>
    </div>
  );
}
