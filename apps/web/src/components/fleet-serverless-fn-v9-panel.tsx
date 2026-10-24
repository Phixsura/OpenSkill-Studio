"use client";
export function FleetServerlessFnV9Panel({ functions, invocations }: { functions: number; invocations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">λ Serverless v9</h3>
    <div className="text-sm">{functions} functions · {invocations.toLocaleString()}/min</div>
  </div>);
}
