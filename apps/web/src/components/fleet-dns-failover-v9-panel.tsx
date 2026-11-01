"use client";
export function FleetDnsFailoverV9Panel({ records, passing }: { records: number; passing: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 DNS Failover v9</h3>
    <div className="text-sm">{records} records · {passing} passing</div>
  </div>);
}
