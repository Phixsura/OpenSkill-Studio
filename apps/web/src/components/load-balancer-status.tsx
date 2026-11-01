"use client";

interface Instance { id: string; status: string; weight_pct: number; }
interface LoadBalancerStatusProps { instances: Instance[]; healthy: number; total: number; }

export function LoadBalancerStatus({ instances, healthy, total }: LoadBalancerStatusProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Load Balancer</h3>
        <span className={`text-sm font-medium ${healthy === total ? "text-green-600" : "text-yellow-600"}`}>
          {healthy}/{total} healthy
        </span>
      </div>
      <ul className="mt-3 space-y-1">
        {instances.map(i => (
          <li key={i.id} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${i.status === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono text-xs">{i.id}</span>
            </span>
            <span className="text-xs text-gray-400">{i.weight_pct}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
