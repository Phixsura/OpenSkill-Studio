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

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function LoadBalancerCard({ instances, appName }: LoadBalancerCardProps) {
  const healthyCount = instances.filter((i) => i.healthy).length;
  const totalRequests = instances.reduce((s, i) => s + i.request_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Load Balancer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              healthyCount === instances.length
                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
            }`}
          >
            {healthyCount}/{instances.length} healthy
          </span>
          <span className="text-xs text-gray-400">{formatNum(totalRequests)} req</span>
        </div>
      </div>

      {instances.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No instances</p>
      ) : (
        <div className="space-y-1.5">
          {instances.map((i) => (
            <div
              key={i.instance_id}
              className={`flex items-center justify-between rounded px-2.5 py-2 ${
                i.healthy
                  ? "hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  : "bg-red-50/50 dark:bg-red-950/10"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${i.healthy ? "bg-green-500" : "bg-red-500"}`}
                />
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {i.address}
                </span>
                {i.weight > 1 && <span className="text-[10px] text-gray-400">w{i.weight}</span>}
              </div>
              <span className="text-[11px] text-gray-400">{formatNum(i.request_count)} req</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
