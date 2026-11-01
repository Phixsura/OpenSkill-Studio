"use client";
export function FleetApiTrafficControlV9Panel({ controls, rps }: { controls: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 Traffic Control v9</h3>
    <div className="text-sm">{controls} controls · {rps.toLocaleString()} rps</div>
  </div>);
}
