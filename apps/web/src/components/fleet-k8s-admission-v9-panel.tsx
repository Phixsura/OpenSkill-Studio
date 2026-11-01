"use client";
export function FleetK8sAdmissionV9Panel({ webhooks, denied }: { webhooks: number; denied: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ K8s Admission v9</h3>
    <div className="text-sm">{webhooks} webhooks · {denied} denied</div>
  </div>);
}
