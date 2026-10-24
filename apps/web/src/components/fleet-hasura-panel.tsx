"use client";
export function FleetHasuraPanel({ instances, healthy, tables, requests }: { instances: number; healthy: number; tables: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">◆ Hasura</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {tables} tables · {requests.toLocaleString()} req</div>
  </div>);
}
