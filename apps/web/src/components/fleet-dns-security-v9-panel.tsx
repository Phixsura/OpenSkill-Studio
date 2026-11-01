"use client";
export function FleetDnsSecurityV9Panel({ zones, dnssec }: { zones: number; dnssec: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 DNS Security v9</h3>
    <div className="text-sm">{zones} zones · {dnssec} DNSSEC</div>
  </div>);
}
