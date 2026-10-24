"use client";
export function FleetDnsMonitorV9Panel({ domains, failures }: { domains: number; failures: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 DNS Monitor v9</h3>
    <div className="text-sm">{domains} domains · {failures} failures</div>
  </div>);
}
