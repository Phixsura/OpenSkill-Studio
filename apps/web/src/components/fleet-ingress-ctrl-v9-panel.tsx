"use client";
export function FleetIngressCtrlV9Panel({ rules, rps }: { rules: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 Ingress Controller v9</h3>
    <div className="text-sm">{rules} rules · {rps.toLocaleString()} rps</div>
  </div>);
}
