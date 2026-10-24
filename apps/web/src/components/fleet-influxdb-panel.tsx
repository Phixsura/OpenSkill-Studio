"use client";
export function FleetInfluxdbPanel({ instances, healthy, series, writesPerSec }: { instances: number; healthy: number; series: number; writesPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 InfluxDB</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {series.toLocaleString()} series · {writesPerSec.toLocaleString()} w/s</div>
  </div>);
}
