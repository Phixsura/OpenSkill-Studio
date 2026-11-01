"use client";
export function FleetBackpressurePanel({ total, pressured, dropped, stable }: { total: number; pressured: number; dropped: number; stable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⬇️ Backpressure</h3>
    {stable ? <span className="text-xs text-green-600">✅ No backpressure</span>
     : <span className="text-xs text-red-500">⚠️ {pressured} queues pressured · {dropped.toLocaleString()} dropped</span>}
  </div>);
}
