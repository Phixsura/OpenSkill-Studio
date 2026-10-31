"use client";
export function FleetTrpcPanel({ routers, procedures, calls, errors }: { routers: number; procedures: number; calls: number; errors: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 tRPC</h3>
    <div className="text-sm">{routers} routers · {procedures} procedures · {calls.toLocaleString()} calls</div>
    {errors > 0 && <span className="text-xs text-red-500">⚠️ {errors} errors</span>}
  </div>);
}
