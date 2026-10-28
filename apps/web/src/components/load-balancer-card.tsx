"use client";

interface InstanceInfo {
  instance_id: string;
  address: string;
  weight: number;
  healthy: boolean;
  request_count: number;
}

interface LoadBalancerCardProps {
  instances: InstanceInfo[];
  appName: string;
}

export default function LoadBalancerCard({ instances, appName }: LoadBalancerCardProps) {
  const healthy = instances.filter((i) => i.healthy).length;
  const totalRequests = instances.reduce((s, i) => s + i.request_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⚖️ Load Balancer
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {healthy}/{instances.length} healthy · {totalRequests} reqs
        </span>
      </div>

      {instances.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No backend instances</p>
      ) : (
        <div className="space-y-1.5">
          {instances.map((i) => (
            <div
              key={i.instance_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${i.healthy ? "bg-green-500" : "bg-red-500"}`}
                />
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {i.address}
                </span>
                {i.weight > 1 && <span className="text-[9px] text-gray-400">w{i.weight}</span>}
              </div>
              <span className="text-[11px] text-gray-400">{i.request_count} reqs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
