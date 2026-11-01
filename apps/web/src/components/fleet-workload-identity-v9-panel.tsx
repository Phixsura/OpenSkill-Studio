"use client";
export function FleetWorkloadIdentityV9Panel({ workloads, federated }: { workloads: number; federated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪪 Workload Identity v9</h3>
    <div className="text-sm">{workloads} workloads · {federated} federated</div>
  </div>);
}
