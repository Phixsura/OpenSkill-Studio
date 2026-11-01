"use client";
export function FleetClickhousePanel({ shards, healthy, totalRows, qps }: { shards: number; healthy: number; totalRows: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 ClickHouse</h3>
    <div className="text-sm">{healthy}/{shards} healthy · {totalRows.toLocaleString()} rows · {qps} qps</div>
  </div>);
}
