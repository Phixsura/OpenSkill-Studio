"use client";
export function FleetMetricsSrvPanel({ instances, healthy, nodesScraped, scrapeInterval }: { instances: number; healthy: number; nodesScraped: number; scrapeInterval: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 metrics-server</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {nodesScraped} nodes · {scrapeInterval}s interval</div>
  </div>);
}
