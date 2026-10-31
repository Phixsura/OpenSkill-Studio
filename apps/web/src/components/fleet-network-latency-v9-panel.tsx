"use client";
export function FleetNetworkLatencyV9Panel({ paths, avg }: { paths: number; avg: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Network Latency v9</h3>
    <div className="text-sm">{paths} paths · {avg}ms avg</div>
  </div>);
}
