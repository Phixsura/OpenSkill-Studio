"use client";
export function FleetYugabytePanel({ clusters, running, tablets, tservers }: { clusters: number; running: number; tablets: number; tservers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟣 YugabyteDB</h3>
    <div className="text-sm">{running}/{clusters} running · {tablets.toLocaleString()} tablets · {tservers} tservers</div>
  </div>);
}
