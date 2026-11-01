"use client";
export function FleetProgressiveDeliveryV9Panel({ rollouts, inProgress }: { rollouts: number; inProgress: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Progressive Delivery v9</h3>
    <div className="text-sm">{rollouts} rollouts · {inProgress} in progress</div>
  </div>);
}
