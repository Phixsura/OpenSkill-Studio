"use client";
export function FleetDnsResolverV9Panel({ zones, qps }: { zones: number; qps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 DNS Resolver v9</h3>
    <div className="text-sm">{zones} zones · {qps.toLocaleString()} qps</div>
  </div>);
}
