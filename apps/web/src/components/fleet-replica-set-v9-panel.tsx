"use client";
export function FleetReplicaSetV9Panel({ sets, ready }: { sets: number; ready: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Replica Set v9</h3>
    <div className="text-sm">{sets} sets · {ready} ready</div>
  </div>);
}
