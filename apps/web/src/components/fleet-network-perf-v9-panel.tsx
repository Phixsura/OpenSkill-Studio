"use client";
export function FleetNetworkPerfV9Panel({ links, latency }: { links: number; latency: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Network Perf v9</h3>
    <div className="text-sm">{links} links · {latency}ms avg</div>
  </div>);
}
