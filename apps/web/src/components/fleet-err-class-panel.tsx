"use client";
export function FleetErrClassPanel({ total, clientErrors, serverErrors }: { total: number; clientErrors: number; serverErrors: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Error Classification</h3>
    <div className="text-sm">{total} errors · {clientErrors} client (4xx) · {serverErrors} server (5xx)</div>
  </div>);
}
