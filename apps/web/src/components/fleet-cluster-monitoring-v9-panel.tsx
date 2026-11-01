"use client";
export function FleetClusterMonitoringV9Panel({ clusters, alerts }: { clusters: number; alerts: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Cluster Monitoring v9</h3>
    <div className="text-sm">{clusters} clusters · {alerts} alerts</div>
  </div>);
}
