"use client";
export function FleetQueueWaitPanel({ services, avgWait, p99Wait, acceptable }: { services: number; avgWait: number; p99Wait: number; acceptable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏳ Queue Wait Time</h3>
    <div className="text-sm">avg {avgWait}ms · p99 {p99Wait}ms · {services} services</div>
    {!acceptable && <span className="text-xs text-red-500">⚠️ High queue wait</span>}
  </div>);
}
