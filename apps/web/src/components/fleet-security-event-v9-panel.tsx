"use client";
export function FleetSecurityEventV9Panel({ total, critical }: { total: number; critical: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Security Event v9</h3>
    <div className="text-sm">{total} events · {critical} critical</div>
  </div>);
}
