"use client";
export function FleetAutoScalerV9Panel({ targets, replicas }: { targets: number; replicas: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Auto Scaler v9</h3>
    <div className="text-sm">{targets} targets · {replicas} replicas</div>
  </div>);
}
