"use client";
export function FleetAdmissionPanel({ webhooks, totalCalls, denied, errors, healthy }: { webhooks: number; totalCalls: number; denied: number; errors: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Admission Control</h3>
    <div className="text-sm">{totalCalls.toLocaleString()} calls · {denied} denied · {errors} errors</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ Webhook errors</span>}
  </div>);
}
