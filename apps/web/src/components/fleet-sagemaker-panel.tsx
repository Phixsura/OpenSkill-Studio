"use client";
export function FleetSagemakerPanel({ endpoints, inService, instances, invocations }: { endpoints: number; inService: number; instances: number; invocations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 SageMaker</h3>
    <div className="text-sm">{inService}/{endpoints} serving · {instances} instances · {invocations.toLocaleString()} inv</div>
  </div>);
}
