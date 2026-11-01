"use client";
export function FleetK8sOperatorV9Panel({ operators, reconciles }: { operators: number; reconciles: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ K8s Operator v9</h3>
    <div className="text-sm">{operators} operators · {reconciles}/min reconciles</div>
  </div>);
}
